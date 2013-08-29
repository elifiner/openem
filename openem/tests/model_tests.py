# coding=utf8
from django.test import TestCase
from openem.models import User, Conversation, Message, Visit

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

class VisitTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='123456')
        self.user2 = User.objects.create_user(username='user2', password='123456')
        self.user3 = User.objects.create_user(username='user3', password='123456')
        self.conv1 = Conversation.objects.create(owner=self.user1, title='some title')
        self.conv2 = Conversation.objects.create(owner=self.user2, title='another title')
        Message.objects.create(conversation=self.conv1, author=self.user1, text='hello')
        Message.objects.create(conversation=self.conv1, author=self.user2, text='hey')
        Message.objects.create(conversation=self.conv1, author=self.user1, text='how are you?')
        Message.objects.create(conversation=self.conv1, author=self.user2, text="i'm good")
        Message.objects.create(conversation=self.conv1, author=self.user3, text="don't forget me")
        Message.objects.create(conversation=self.conv2, author=self.user1, text='howdy')
        Message.objects.create(conversation=self.conv2, author=self.user2, text='yowdy')
        Message.objects.create(conversation=self.conv2, author=self.user1, text="how y'all are?")
        Message.objects.create(conversation=self.conv2, author=self.user2, text="neva betta")

    def test_should_return_all_messages_before_marking(self):
        messages = self.conv1.unread_messages(for_user=self.user1)
        self.assertEquals(len(messages), 5)

    def test_should_return_no_messages_after_marking(self):
        self.user1.mark_visited(self.conv1)
        messages = self.conv1.unread_messages(for_user=self.user1)
        self.assertEquals(len(messages), 0)

    def test_should_return_new_messages_after_marking_and_posting(self):
        self.user1.mark_visited(self.conv1)
        Message.objects.create(conversation=self.conv1, author=self.user2, text='so am i')
        messages = self.conv1.unread_messages(for_user=self.user1)
        self.assertEquals(len(messages), 1)

    def test_should_return_all_conversations_before_marking(self):
        convs = self.user1.all_unread_conversations()
        self.assertEquals(len(list(convs)), 2)

    def test_should_return_unread_conversations_after_marking(self):
        self.user1.mark_visited(self.conv1)
        convs = self.user1.all_unread_conversations()
        self.assertEquals(len(list(convs)), 1)

    def test_should_return_my_conversations_before_marking(self):
        # self.user1.mark_visited(self.conv1)
        convs = self.user3.my_unread_conversations()
        self.assertEquals(len(list(convs)), 1)

    def test_should_return_my_unread_conversations_after_marking(self):
        self.user3.mark_visited(self.conv1)
        convs = self.user3.my_unread_conversations()
        self.assertEquals(len(list(convs)), 0)
