import re
from datetime import datetime

from django.db import models
from django.contrib import auth
from django.db.models import F

from openem import utils
from openem.middlewares import get_current_user

class User(auth.models.AbstractUser):
    def all_unread_conversations(self):
        visited = self.visits.filter(visit_time__gte=F('conversation__update_time')).all()
        exclude = [v.conversation_id for v in visited]
        # FIXME: this exclude may cause issues if number of visited conversations is very high
        return Conversation.objects.exclude(id__in=exclude)

    def my_unread_conversations(self):
        return self.all_unread_conversations().filter(messages__author=self)

    def pending_unread_conversations(self):
        return self.all_unread_conversations().filter(status=Conversation.STATUS.PENDING)

    def my_conversations(self):
        return Conversation.objects.filter(messages__author=self)

    def mark_visited(self, conversation):
        conversation.update_time = conversation.messages.last.post_time
        conversation.save()
        Visit.objects.set(conversation=conversation, user=self, visit_time=conversation.update_time)

class Conversation(models.Model):
    class STATUS(object):
        PENDING = 'pending'
        ACTIVE = 'active'

    start_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(Conversation, self).__init__(*args, **kwargs)
        if not self.start_time:
            self.start_time = datetime.utcnow()
        if not self.update_time:
            self.update_time = self.start_time
        if not self.status:
            self.status = self.STATUS.PENDING

    def __unicode__(self):
        return self.title

    @property
    def start_time_since(self):
        return utils.prettydate(self.start_time)

    @property
    def update_time_since(self):
        return utils.prettydate(self.update_time)

    @property
    def slug(self):
        return re.compile('\W+', re.UNICODE).sub('_', self.title)

    def unread_messages_for_user(self, user):
        qs = self.messages.all()
        visit = self.visits.filter(user=user)
        if visit:
            qs = qs.filter(post_time__gt=visit[0].visit_time)
        return qs

    def unread_messages(self):
        messages = list(self.unread_messages_for_user(get_current_user()))
        if not messages and self.messages:
            messages = [self.messages.last]
        return messages

    @property
    def read_class(self):
        return '' if self.unread_messages_for_user(get_current_user()).exists() else 'read'

class MessageManager(models.Manager):
    @property
    def preview(self):
        return self.get_query_set()[:2]

    @property
    def last(self):
        return self.get_query_set().reverse()[0]

    def updated(self, after_message_id, for_user):
        qs = self.get_query_set().filter(id__gt = after_message_id)
        qs = qs.exclude(author_id = for_user.id)
        return qs

class Message(models.Model):
    class Meta:
        ordering = ['post_time']

    class TYPE(object):
        TALKER = 'talker'
        LISTENER = 'listener'

    objects = MessageManager()

    post_time = models.DateTimeField(db_index=True)
    text = models.TextField()
    conversation = models.ForeignKey('Conversation', related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        if not self.post_time:
            self.post_time = datetime.utcnow()
        if self.conversation:
            self.conversation.update_time = self.post_time

    def __unicode__(self):
        return self.text

    @property
    def type(self):
        if not self.conversation:
            raise ValueError('message not connected to conversation')
        if self.author == self.conversation.owner:
            return Message.TYPE.TALKER
        else:
            return Message.TYPE.LISTENER

    @property
    def post_time_since(self):
        return utils.prettydate(self.post_time)

    @property
    def html_text(self):
        return utils.text2p(self.text)

    def is_unread_by(self, user):
        visited = self.conversation.visits.filter(user=user)
        return not visited or self.post_time > visited[0].visit_time

    @property
    def read_class(self):
        return '' if self.is_unread_by(get_current_user()) else 'read'

class VisitManager(models.Manager):
    def set(self, conversation, user, visit_time):
        try:
            visit = self.get_query_set().filter(conversation=conversation, user=user)[0]
        except IndexError:  
            visit = Visit(conversation=conversation, user=user)
        visit.visit_time = visit_time
        visit.save()

class Visit(models.Model):
    class Meta:
        unique_together = ('user', 'conversation')
    objects = VisitManager()
    user = models.ForeignKey(User, related_name='visits', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='visits', on_delete=models.CASCADE)
    visit_time = models.DateTimeField()
