from django.conf.urls import patterns, include, url
from openem import views

urlpatterns = patterns('',
    url(r'^$', views.landing),
)
