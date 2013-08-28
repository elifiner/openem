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
    def all_messages(self):
        return self.messages.all()

    @property
    def first_messages(self):
        return self.messages.all()[:2]

    @property
    def last_message_id(self):
        return self.messages.reverse()[0]

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

    # def get_first_message(self):
    #     return self.messages.first()

    # def get_last_message(self):
    #     return db.session.query(Message).filter_by(conversation_id=self.id).order_by(Message.id.desc()).first()

    # def get_updated_messages(self, last_message_id, for_user=None):
    #     q = self.messages.filter(Message.id > last_message_id)
    #     if for_user:
    #         q = q.filter(Message.author_id != for_user.id)
    #     return q.all()

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

    # @classmethod
    # def all(cls):
    #     return cls.query.order_by(cls.update_time.desc()).all()

class Message(models.Model):
    class TYPE(object):
        TALKER = 'talker'
        LISTENER = 'listener'

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

    # def __json__(self):
    #     data = super(Message, self).__json__()
    #     data['author'] = self.author.name
    #     data['type'] = self.type
    #     data['unescaped_text'] = self.unescaped_text
    #     return data

    # @property
    # def type(self):
    #     if not self.conversation:
    #         raise ValueError('message not connected to conversation')

    #     if self.author is self.conversation.owner:
    #         return Message.TYPE.TALKER
    #     else:
    #         return Message.TYPE.LISTENER

    @property
    def post_time_since(self):
        return utils.prettydate(self.post_time)

    # @property
    # def read_class(self):
    #     return '' if self.is_unread_by(User.get_current()) else 'read'

    @property
    def unescaped_text(self):
        return utils.unescape(self.text)

    # def is_unread_by(self, user):
    #     unread = Unread.get(user.id, self.conversation_id)
    #     return unread is None or self.id > unread.last_read_message_id

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
