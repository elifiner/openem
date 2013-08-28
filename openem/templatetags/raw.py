from django import template
from django.template.loaders.app_directories import Loader

register = template.Library()
 
@register.tag('include_raw')
def include_raw(parser, token):
    try:
        tag, name= token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r takes one argument: the name of the template to be included" % tag
    name = name.strip("'\"")        
    source, _ = Loader().load_template_source(name)
    return template.TextNode(source)
