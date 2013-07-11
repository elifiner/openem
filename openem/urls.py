from django.conf.urls import patterns, include, url
from openem import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^login$', views.login),
    url(r'^conversations/(?P<id>\d+)/$', views.conversation),
)
