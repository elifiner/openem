from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from openem import models, forms

def index(request):
    conversations = models.Conversation.objects.all()
    return render(request, 'landing.html', {
        'conversations': conversations
    })

def login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            return HttpResponse('YES!')
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {
        'form': form
    })

def conversation(request, id):
    conversation = get_object_or_404(models.Conversation, pk=id)
    return render(request, 'conversation.html', {
        'conversation': conversation,
        'logged_in_user': '',
        'user_message_type': ''
    })
