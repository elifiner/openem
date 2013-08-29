import re
from django.db import models
from openem import utils
from datetime import datetime

from django.contrib import auth
from django.db.models import F, Q

class User(auth.models.AbstractUser):
    def unread_conversations(self):
        qs = Conversation.objects.filter(
            Q(visit__user__isnull=True) | Q(visit__user=self),
            Q(visit__visit_time__isnull=True) | Q(update_time__gt=F('visit__visit_time')),
        )
        return qs

    def visited(self, conversation):
        Visit.objects.set(conversation=conversation, user=self, visit_time=conversation.update_time)

class Conversation(models.Model):
    class STATUS(object):
        PENDING = 'pending'
        ACTIVE = 'active'

    start_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='conversations', on_delete=models.CASCADE)

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

    def unread_messages(self, for_user):
        qs = self.messages.all()
        visit = self.visit.filter(user=for_user)
        if visit:
            qs = qs.filter(post_time__gt=visit[0].visit_time)
        return qs

    # @property
    # def read_class(self):
    #     return '' if self.get_unread_messages(User.get_current()).count() else 'read'

    # @property
    # def unread_messages(self):
    #     return self.get_unread_messages(User.get_current(), include_last_read=True)

    # def get_unread_messages(self, for_user, include_last_read=False):
    #     unread = Unread.get(for_user.id, self.id)
    #     last_read_message_id = unread.last_read_message_id if unread else 0
    #     if include_last_read:
    #         # return the last read message as well
    #         return self.messages.filter(Message.id >= last_read_message_id)
    #     else:
    #         return self.messages.filter(Message.id > last_read_message_id)

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
    user = models.ForeignKey(User, related_name='visit', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='visit', on_delete=models.CASCADE)
    visit_time = models.DateTimeField()
