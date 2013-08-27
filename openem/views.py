# coding=utf8

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from openem import models, forms

User = auth.models.User

def index(request):
    conversations = models.Conversation.objects.all()
    if request.user.is_authenticated():
        return render(request, 'profile.html', {
            # FIXME: get actual message counts
            'user': request.user,
            'my_updated': 0, 
            'all_updated': 0, 
            'pending': 0,
        })
    else:
        return render(request, 'landing.html', {
            'conversations': conversations
        })

def login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.username, password=form.password)
            if user:
                auth.login(request, user)
                return redirect(request.GET.get('next', '/'))
            else:
                # FIXME: use gettext translation here
                form.add_error(u'הסיסמא לא נכונה, נסו שנית.')
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {
        'form': form
    }, status=form.get_status())

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('next', '/'))

def register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.username)
            except User.DoesNotExist:
                user = User.objects.create_user(username=form.username, password=form.password, email=form.email)
                user.save()
                user = auth.authenticate(username=form.username, password=form.password)
                auth.login(request, user)
                return redirect(request.GET.get('next', '/'))
            else:
                # user already exists
                form.add_error(u'מישהו כבר נרשם עם השם %s' % form.username)
    else:
        form = forms.RegisterForm()

    return render(request, 'register.html', {
        'form': form
    }, status=form.get_status())

def conversation(request, id, slug=None):
    conv = get_object_or_404(models.Conversation, pk=id)
    if slug != conv.slug:
        return redirect(conversation, id=id, slug=conv.slug)
    return render(request, 'conversation.html', {
        'conversation': conv,
        'logged_in_user': request.user,
        'user_message_type': ''
    })

def document(request, name):
    return render(request, 'docs/%s.html' % name)
