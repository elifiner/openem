# coding=utf8

import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
from django.forms.models import model_to_dict

from openem import models, forms

def index(request):
    conversations = models.Conversation.objects.all()
    if request.user.is_authenticated():
        return render(request, 'profile.html', {
            # FIXME: get actual message counts
            'user': request.user,
            'my_updated': request.user.my_unread_conversations().count(),
            'all_updated': request.user.all_unread_conversations().count(),
            'pending': request.user.pending_unread_conversations().count(),
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
                user = models.User.objects.get(username=form.username)
            except models.User.DoesNotExist:
                user = models.User.objects.create_user(username=form.username, password=form.password, email=form.email)
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

def document(request, name):
    return render(request, 'docs/%s.html' % name)

@login_required
def conversation(request, id, slug=None):
    conv = get_object_or_404(models.Conversation, pk=id)
    if slug != conv.slug:
        return redirect(conversation, id=id, slug=conv.slug)
    request.user.mark_visited(conv)
    return render(request, 'conversation.html', {
        'conversation': conv,
        'logged_in_user': request.user,
        'user_message_type': get_message_type(conv, request.user)
    })

@login_required
@transaction.commit_on_success
def post_message(request, id, slug):
    conv = get_object_or_404(models.Conversation, pk=id)
    message = request.POST.get('message')
    if not message:
        return HttpResponseBadRequest()
    if (conv.owner != request.user and conv.status == models.Conversation.STATUS.PENDING):
        conv.status = models.Conversation.STATUS.ACTIVE
    models.Message.objects.create(author=request.user, conversation=conv, text=message)

    request.user.mark_visited(conv)
    conv.update_time = datetime.utcnow()
    conv.save()

    # FIXME: uncomment to send email updates
    # send_email_updates(conv, message, user)

    return redirect('/conversations/%s/%s/#bottom' % (id, slug))

@login_required
@transaction.commit_on_success
def new_conversation(request):
    if request.method == 'POST':
        form = forms.NewConversationForm(request.POST)
        if form.is_valid():
            conv = models.Conversation.objects.create(owner=request.user, title=form.title)
            models.Message.objects.create(author=request.user, conversation=conv, text=form.message)
            request.user.mark_visited(conv)
            # FIXME: uncomment to send email updates
            # send_email_updates(conv, message, user)
            return redirect(conversation, id=conv.id, slug=conv.slug)
    else:
        form = forms.NewConversationForm()

    return render(request, 'new_conversation.html', {
        'form': form
    }, status=form.get_status())

@login_required
@transaction.commit_on_success
def conversation_updates(request, id, slug):
    conv = get_object_or_404(models.Conversation, pk=id)
    last_message_id = int(request.GET.get('last_message_id', 0))
    messages = list(conv.messages.updated(last_message_id, request.user))
    last_message_id = messages[-1].id if messages else last_message_id

    # mark conversation as read
    # request.user.mark_visited(conv)

    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
    result = json.dumps(dict(
        conversation=model_to_dict(conv),
        messages=[model_to_dict(m) for m in messages],
        last_message_id=last_message_id
    ), default=dthandler)
    return HttpResponse(result, content_type='application/json',)

@login_required
def all_conversations(request):
    return render(request, 'updates.html', {
        'title': u"כל השיחות",
        'conversations': models.Conversation.objects.all()
    })

@login_required
def my_conversations(request):
    return render(request, 'updates.html', {
        'title': u"השיחות שלי",
        'conversations': request.user.my_conversations()
    })

@login_required
def pending_conversations(request):
    return render(request, 'updates.html', {
        'title': u"שיחות ממתינות",
        'conversations': models.Conversation.objects.filter(status=models.Conversation.STATUS.PENDING)
    })

def get_message_type(conv, user):
    if conv.owner == user:
        return models.Message.TYPE.TALKER
    else:
        return models.Message.TYPE.LISTENER
