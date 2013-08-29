# coding=utf8
import os
import re
import time
import random
import requests
from urlparse import urljoin

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def verify(actual, expected):
    if not isinstance(expected, list):
        expected = [expected]
    if actual not in expected:
        raise AssertionError('expected=%r, actual=%r' % (expected, actual))

class Session(requests.Session):
    def get(self, *args, **kwargs):
        ret = super(Session, self).get(*args, **kwargs)
        self.csrftoken = self.cookies['csrftoken']
        return ret

    def post(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['csrfmiddlewaretoken'] = self.csrftoken
        return super(Session, self).post(*args, **kwargs)

class Markov(object):
    def __init__(self, text):
        self.cache = {}
        self.words = self.text_to_words(text)
        self.word_size = len(self.words)
        self.database()
        
    def text_to_words(self, text):
        text = re.compile('\W+', re.UNICODE).sub(' ', text)
        return text.split()
    
    def triples(self):
        words = list(self.words) + ['', '']
        for i in range(len(self.words)):
            yield (words[i], words[i+1], words[i+2])

    def database(self):
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]
                
    def generate_markov_text(self, size=25):
        seed = random.randint(0, self.word_size-3)
        seed_word, next_word = self.words[seed], self.words[seed+1]
        w1, w2 = seed_word, next_word
        gen_words = []
        for i in xrange(size):
            gen_words.append(w1)
            w1, w2 = w2, random.choice(self.cache[(w1, w2)])
        gen_words.append(w2)
        return ' '.join(gen_words)

class User(object):
    class Conversation():
        def __init__(self, user, url):
            self.user = user
            self.session = user.session
            self.url = url

        def send(self, message):
            print ('** %s **\n%s\n' % (self.user.username[::-1], message[::-1])).encode('utf8')
            r = self.session.post(urljoin(self.url, 'post'), allow_redirects=False, 
                data=dict(message=message))
            verify(r.status_code, 302)

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = Session()
        self.session.get(self.url) # store csrftoken

    def register(self):
        r = self.session.post(self.url + '/register/', allow_redirects=False,
            data=dict(username=self.username, password=self.password, password2=self.password))
        verify(r.status_code, [302, 400]) # ignore duplicate registrations

    def login(self):
        r = self.session.post(self.url + '/login/', allow_redirects=False,
            data=dict(username=self.username, password=self.password))
        verify(r.status_code, 302)

    def share(self, title, message):
        r = self.session.post(self.url + '/conversations/new', allow_redirects=False,
            data=dict(title=title, message=message))
        verify(r.status_code, 302)
        return self.Conversation(self, r.headers['location'])

    def open(self, url):
        return self.Conversation(self, url)

def simulate(url):
    markov = Markov(open(os.path.join(APP_ROOT, 'corpus.txt')).read().decode('utf8'))
    # lorem_ipsum = open('lorem.txt').read().decode('utf8').splitlines()

    def random_line():
        return markov.generate_markov_text(random.randint(5, 15))

    def random_message():
        # return '\n'.join(random.sample(lorem_ipsum, random.randint(2, 7)))
        lines = []
        for i in xrange(random.randint(2, 7)):
            lines.append(random_line())
        return '\n'.join(lines)

    users = [
        User(url, u'מימי תעסק', u'123456'),
        User(url, u'דפנה קי', u'123456'),
        User(url, u'מילי גרם', u'123456'),
        User(url, u'עלילה מסלול', u'123456'),
        User(url, u'תיקי פור', u'123456'),
    ]

    for user in users:
        user.register()
        user.login()

    while True:
        # choose two users
        user1 = random.choice(users)
        user2 = random.choice(list(u for u in users if u is not user1))

        # start a conversation
        user1conv = user1.share(random_line(), random_message())
        user2conv = user2.open(user1conv.url)

        # converse
        for i in xrange(random.randint(5, 15)):
            user2conv.send(random_message())
            time.sleep(10.0)
            user1conv.send(random_message())
            time.sleep(10.0)

if __name__ == '__main__':
    simulate('http://localhost:8000')
