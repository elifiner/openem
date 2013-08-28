import re
from django.db import models
from openem import utils
from datetime import datetime

from django.contrib.auth.models import User

class Conversation(models.Model):
    class STATUS(object):
        PENDING = 'pending'
        ACTIVE = 'active'

    start_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='conversations')

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

    # def mark_read(self, user):
    #     if user:
    #         Unread.set(user.id, self.id, self.get_last_message().id)

class MessageManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        qs = super(MessageManager, self).get_query_set()
        return qs.order_by('post_time')

    def preview(self):
        return self.get_query_set()[:2]

    def last(self):
        return self.get_query_set().reverse()[0]  

    def updated(self, after_message_id, for_user):
        qs = self.get_query_set().filter(id__gt = after_message_id)
        qs = qs.exclude(author_id = for_user.id)
        return qs

class Message(models.Model):
    class TYPE(object):
        TALKER = 'talker'
        LISTENER = 'listener'

    objects = MessageManager()

    post_time = models.DateTimeField(db_index=True)
    text = models.TextField()
    conversation = models.ForeignKey('Conversation', related_name='messages')
    author = models.ForeignKey(User)

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

# class Unread(db.Model, Jsonable):
#     __tablename__ = 'unread'
#     __table_args__ = (db.PrimaryKeyConstraint('user_id', 'conversation_id'), {})

#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
#     conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), index=True)
#     last_read_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), index=True)

#     def __init__(self, user_id, conversation_id):
#         self.user_id = user_id
#         self.conversation_id = conversation_id

#     def __repr__(self):
#         return '<Unread (user=%s, conversation=%s, message=%s)>' % \
#             (self.user_id, self.conversation_id, self.last_read_message_id)

#     @classmethod
#     def get(cls, user_id, conversation_id):
#         return cls.query.filter_by(user_id=user_id, conversation_id=conversation_id).first()

#     @classmethod
#     def set(cls, user_id, conversation_id, last_read_message_id):
#         unread = cls.get(user_id, conversation_id)
#         if unread is None:
#             unread = cls(user_id, conversation_id)
#             db.session.add(unread)
#         unread.last_read_message_id = last_read_message_id
