from __future__ import unicode_literals

from django.db import models
import uuid
# Create your models here.

class User(models.Model):
    userUniq = models.UUIDField(default=uuid.uuid1, editable=False , primary_key=True)
    userImageUrlLarge = models.URLField(blank=True,max_length=500)
    userImageUrlThumb = models.URLField(blank=True,max_length=500)
    userName = models.CharField(max_length=500,blank=True)
    userEmailfb = models.CharField(max_length=500,unique=True)
    userIdfb = models.CharField(max_length=500,unique=True)
    userAccessTokenfb = models.CharField(max_length=500,blank=False,default="")
    userCreatedTime = models.DateTimeField('User Created')
    fbTotalFriends = models.BigIntegerField(editable=True,blank=True,default=0)
    def __str__(self):              # __unicode__ on Python 2
        return str(self.userUniq) + " " +str(self.userName)

class UserFriends(models.Model):
    user = models.ForeignKey(User)
    username = models.CharField(max_length=200)
    userIdfb = models.CharField(max_length=100,unique=False)
    frUniq = models.UUIDField(default=uuid.uuid1, editable=False)
    time = models.DateTimeField('Friend Created')
    def __str__(self):              # __unicode__ on Python 2
        return str(self.user) + " " +str(self.username)


class Event(models.Model):
    event = models.UUIDField(default=uuid.uuid1, editable=False , primary_key=True)
    eventDetails = models.CharField(max_length=500,blank=True)
    eventName = models.CharField(max_length=100)
    lat = models.CharField(max_length=30,blank=True)
    long = models.CharField(max_length=30,blank=True)
     # Created by ashish
    eventImage = models.URLField(blank=True,max_length=500)
    EventCreatedTime = models.DateTimeField('Event Created')
    TotalEventTime = models.IntegerField(editable=True,default=0)
    eventExpired = models.BooleanField(default=False)
    eventCreatedBy = models.CharField(max_length=50,default="")

class userEvent(models.Model):
    user = models.ForeignKey(User)
    event = models.CharField(max_length=50)
    time = models.DateTimeField('Event Signed Up')