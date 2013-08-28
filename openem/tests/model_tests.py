# coding=utf8
from django.test import TestCase
from django.contrib.auth.models import User
from openem.models import Conversation, Message

class ConversationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='123456')
        self.user2 = User.objects.create_user(username='user2', password='123456')
        self.conv = Conversation.objects.create(owner=self.user1, title='some title')
        Message.objects.create(conversation=self.conv, author=self.user1, text='hello')
        Message.objects.create(conversation=self.conv, author=self.user2, text='hey')
        Message.objects.create(conversation=self.conv, author=self.user1, text='how are you?')
        Message.objects.create(conversation=self.conv, author=self.user2, text="i'm good")

    def test_should_return_no_messages_for_empty_conversation(self):
        user = User.objects.create_user(username='user', password='123456')
        conv = Conversation.objects.create(owner=user, title='some title')
        messages = conv.messages.updated(after_message_id=0, for_user=user)
        self.assertEquals(len(messages), 0)

    def test_should_return_no_messages_after_last_message(self):
        messages = self.conv.messages.updated(after_message_id=4, for_user=self.user1)
        self.assertEquals(len(messages), 0)
        messages = self.conv.messages.updated(after_message_id=4, for_user=self.user2)
        self.assertEquals(len(messages), 0)

    def test_should_return_all_other_user_messages_after_0_message(self):
        messages = self.conv.messages.updated(after_message_id=0, for_user=self.user1)
        self.assertEquals(len(messages), 2)
        self.assertEquals(messages[0].text, 'hey')
        self.assertEquals(messages[1].text, "i'm good")

    def test_should_return_new_messages(self):
        messages = self.conv.messages.updated(after_message_id=2, for_user=self.user1)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].text, "i'm good")
