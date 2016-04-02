from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signup, name='fbSignUp'),
    url(r'^createEvent/$', views.createEvent, name='createEvent'),
    url(r'^getEvents/$', views.getEvent, name='getEvents'),
    url(r'^signUpEvent/$', views.SignupEvent, name='SignUpEvent'),
    url(r'^getProfile/$', views.getUserInfo, name='getProfile'),
    ]