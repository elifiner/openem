import re
from django.db import models
from openem import utils
from datetime import datetime

from django.contrib import auth

class User(auth.models.AbstractUser):
    def unread_conversations(self):
        # get all the conversations that have at least one unread message
        # whose id is heigher than what's recorded in last_read
        qs = Conversation.objects.raw("""
            select *
            from openem_conversation
            left outer join openem_lastread
                on (openem_conversation.id = openem_lastread.conversation_id)
            inner join (
                    select conversation_id, max(id) as id
                    from openem_message group by conversation_id
                ) as max_message
                on (openem_conversation.id = max_message.conversation_id)
            where max_message.id > coalesce(openem_lastread.message_id, 0)
        """)
        return list(qs)

    @property
    def conversations(self):
        return self.conversations.filter(message__author=self).distinct()

    def mark_all_read(self, conversation):
        """
        Marks the conversation and all its messages as read.
        """
        LastRead.objects.set(conversation=conversation, user=self, message=conversation.messages.last)

class Conversation(models.Model):
    class STATUS(object):
        PENDING = 'pending'
        ACTIVE = 'active'

    start_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owned_conversations', on_delete=models.CASCADE)

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
        last_read = self.last_read.filter(user=for_user)
        if last_read:
            qs = qs.filter(id__gt=last_read[0].message.id)
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

class LastReadManager(models.Manager):
    def set(self, conversation, user, message):
        try:
            last_read = self.get_query_set().filter(conversation=conversation, user=user)[0]
        except IndexError:  
            last_read = LastRead(conversation=conversation, user=user)
        last_read.message = message
        last_read.save()

class LastRead(models.Model):
    class Meta:
        unique_together = ('user', 'conversation')
    objects = LastReadManager()
    user = models.ForeignKey(User, related_name='last_read', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='last_read', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
