from django.http import HttpResponse
from django.template import Context, loader

def landing(request):
    template = loader.get_template('landing.html')
    return HttpResponse(template.render(Context({})))
