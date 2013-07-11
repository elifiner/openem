from django.http import HttpResponse
from django.template import Context, loader
from openem import models

def landing(request):
    template = loader.get_template('landing.html')
    conversations = models.Conversation.objects.all()
    return HttpResponse(template.render(Context({
        'conversations': conversations
    })))
