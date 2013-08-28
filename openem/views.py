# coding=utf8

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
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

@login_required
def conversation(request, id, slug=None):
    conv = get_object_or_404(models.Conversation, pk=id)
    if slug != conv.slug:
        return redirect(conversation, id=id, slug=conv.slug)
    return render(request, 'conversation.html', {
        'conversation': conv,
        'logged_in_user': request.user,
        'user_message_type': ''
    })

@login_required
def new_conversation(request):
    if request.method == 'POST':
        form = forms.NewConversationForm(request.POST)
        if form.is_valid():
            conv = models.Conversation.objects.create(owner=request.user, title=form.title)
            models.Message.objects.create(author=request.user, conversation=conv, text=form.message)
            # FIXME: uncomment to send email updates
            # send_email_updates(conv, message, user)
            return redirect(conversation, id=conv.id, slug=conv.slug)
    else:
        form = forms.NewConversationForm()

    return render(request, 'new_conversation.html', {
        'form': form
    }, status=form.get_status())

def document(request, name):
    return render(request, 'docs/%s.html' % name)
