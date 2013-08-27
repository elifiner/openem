# coding=utf8
from django_webtest import WebTest
from django.contrib.auth.models import User

class IndexTests(WebTest):
    def test_can_get_to_login_page(self):
        resp = self.app.get('/')
        resp = resp.click(href='/login/')
        resp.mustcontain(u'כניסה')

    def test_can_get_to_anon_page(self):
        resp = self.app.get('/')
        resp = resp.click(href='/anon/')
        resp.mustcontain(u'אנונימיות')

    def test_can_get_to_listen_page(self):
        resp = self.app.get('/')
        resp = resp.click(href='/listen/')
        resp.mustcontain(u'הקשבה')

    def test_goes_to_profile_if_logged_in(self):
        User.objects.create_user(username='eli', password='123456').save()
        resp = self.app.get('/', user='eli')
        resp.mustcontain(u'הפרופיל שלי')

class LoginTests(WebTest):
    def test_cant_login_with_no_username(self):
        resp = self.app.get('/login/')
        form = resp.forms['login']
        resp = form.submit(status=400)

    def test_cant_login_with_no_password(self):
        resp = self.app.get('/login/')
        form = resp.forms['login']
        form['username'] = 'eli'
        resp = form.submit(status=400)

    def test_cant_login_with_bad_credentials(self):
        resp = self.app.get('/login/')
        form = resp.forms['login']
        form['username'] = 'eli'
        form['password'] = '123456'
        resp = form.submit(status=400)

    def test_can_login_with_good_credentials(self):
        User.objects.create_user(username='eli', password='123456').save()
        resp = self.app.get('/login/')
        form = resp.forms['login']
        form['username'] = 'eli'
        form['password'] = '123456'
        resp = form.submit().follow()
        resp.mustcontain(u'הפרופיל שלי')

    def test_can_get_to_register_page(self):
        resp = self.app.get('/login/')
        resp = resp.forms['register'].submit()
        resp.mustcontain(u'הצטרפות')

class LogoutTests(WebTest):
    def test_can_logout_after_login(self):
        User.objects.create_user(username='eli', password='123456').save()

        # login
        resp = self.app.get('/login/')
        form = resp.forms['login']
        form['username'] = 'eli'
        form['password'] = '123456'
        resp = form.submit().follow()
        resp.mustcontain(u'הפרופיל שלי')

        # logout
        resp = resp.click(href='/logout/').follow()
        resp.mustcontain(u'שני עקרונות מנחים אותנו')

class RegisterTests(WebTest):
    def test_cant_register_with_no_username(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        resp = form.submit(status=400)

    def test_cant_register_with_no_password(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        form['username'] = 'eli'
        resp = form.submit(status=400)

    def test_cant_register_with_no_password2(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        form['username'] = 'eli'
        form['password'] = '123456'
        resp = form.submit(status=400)

    def test_cant_register_with_different_passwords(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        form['username'] = 'eli'
        form['password'] = '123456'
        form['password2'] = '1234567'
        resp = form.submit(status=400)

    def test_can_register_with_no_email(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        form['username'] = 'eli'
        form['password'] = '123456'
        form['password2'] = '123456'
        resp = form.submit().follow()
        resp.mustcontain(u'הפרופיל שלי')
        assert User.objects.get(username='eli')

    def test_can_register_with_email(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        form['username'] = 'eli'
        form['password'] = '123456'
        form['password2'] = '123456'
        form['email'] = 'eli@momo.com'
        resp = form.submit().follow()
        resp.mustcontain(u'הפרופיל שלי')

    def test_cant_register_with_bad_email(self):
        resp = self.app.get('/register/')
        form = resp.forms['register']
        form['username'] = 'eli'
        form['password'] = '123456'
        form['password2'] = '123456'
        form['email'] = 'eli'
        resp = form.submit(status=400)
