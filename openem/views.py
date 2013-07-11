# coding=utf8

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from openem import models, forms, utils

def index(request):
    conversations = models.Conversation.objects.all()
    user = models.User.get_logged_in(request.session)
    if user:
        return render(request, 'profile.html', {
            # FIXME: get actual message counts
            'user': user,
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
            # FIXME: use gettext translation here
            username, password = form.cleaned_data['name'], form.cleaned_data['password']
            user = models.User.objects.get_or_none(name=username)
            if utils.encrypt_password(password, username) == user.password_hash:
                user.login(request.session)
                return redirect(request.GET.get('goto', '/'))
            else:
                form.add_error(u'הסיסמא לא נכונה, נסו שנית.')
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {
        'form': form
    })

def logout(request):
    user = models.User.get_logged_in(request.session)
    if user:
        user.logout(request.session)
    return redirect(request.GET.get('goto', '/'))

def register(request):
    pass

def conversation(request, id, slug=None):
    conv = get_object_or_404(models.Conversation, pk=id)
    if slug != conv.slug:
        return redirect(conversation, id=id, slug=conv.slug)
    return render(request, 'conversation.html', {
        'conversation': conv,
        'logged_in_user': '',
        'user_message_type': ''
    })

def document(request, name):
    return render(request, '%s.html' % name)