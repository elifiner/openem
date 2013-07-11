from django.conf.urls import patterns, include, url
from openem import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^conversations/(?P<id>\d+)/$', views.conversation),
    url(r'^conversations/(?P<id>\d+)/(?P<slug>\w+)/$', views.conversation),
    url(r'^(?P<name>\w+)/$', views.document),
)
