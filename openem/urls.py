from django.conf.urls import patterns, include, url
from openem import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^register/$', views.register),
    url(r'^conversations/(?P<id>\d+)/$', views.conversation),
    url(r'^conversations/(?P<id>\d+)/(?P<slug>\w+)/$', views.conversation),
    url(r'^conversations/(?P<id>\d+)/(?P<slug>\w+)/post$', views.post_message),
    url(r'^conversations/(?P<id>\d+)/(?P<slug>\w+)/updates$', views.conversation_updates),
    url(r'^conversations/new$', views.new_conversation),
    url(r'^conversations/all$', views.all_conversations),
    url(r'^conversations/pending$', views.pending_conversations),
    url(r'^conversations/my$', views.my_conversations),
    url(r'^(?P<name>\w+)/$', views.document),
)

from django.template.loader import add_to_builtins
add_to_builtins('openem.templatetags.raw')
