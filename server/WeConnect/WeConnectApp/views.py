from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
import json

import facebook
import uuid
from django.utils import timezone
import WeConnectApp.models
import urllib2

from datetime import timedelta

from threading import Thread
def postpone(function):
  def decorator(*args, **kwargs):
    t = Thread(target = function, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
  return decorator

# sample Request
@csrf_exempt
def index(request):
    print "Sample is working"
    data = {'Data': "Hello"}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def signup(request):
    print "Facebook Signing up"
    data = {'UserID': "None", 'UserImage' : "None"}
    # The request will be processed if the request is Post otherwise Bad Request will be returned
    if request.method == 'GET':
        return HttpResponseBadRequest("Get Request not accepted")
    elif request.method == 'POST':
        print "Post Request"
        # print request.POST
        if request.POST.get('name') is None or request.POST.get('emailfb') is None or request.POST.get('id') is None or request.POST.get('fbtoken') is None:
            return HttpResponseBadRequest("Parameter Problem")
        else:
            print "request Recieved"
            userUniqueId = uuid.uuid1()
            time = timezone.now()
            userName = request.POST.get('name')
            userEmailFb = request.POST.get('emailfb')
            userIdFb = request.POST.get('id')
            userImageLarge = getFacebookImageUrlLarge(userIdFb)
            userImageSmall = getFacebookImageUrlSmall(userIdFb)
            userFbToken = request.POST.get('fbtoken')
            data['UserImage'] = str(userImageSmall)
            print userUniqueId,time,userName,userEmailFb,userIdFb,userImageLarge,userImageSmall,userFbToken
            try:
                if WeConnectApp.models.User.objects.filter(userIdfb=userIdFb).exists():
                    print("User Already Registered")
                    user = WeConnectApp.models.User.objects.get(userIdfb=userIdFb)
                    user.userName = userName
                    user.userAccessTokenfb = userFbToken
                    user.userImageUrlThumb = userImageSmall
                    user.userImageUrlLarge = userImageLarge
                    user.userCreatedTime = time
                    userUniqueId = user.userUniq
                    # user.userUniqId = userUniqueId
                    user.save()
                else:
                    print("Creating New User")
                    # print len(userUniqueId),len(userName),len(userEmailFb)
                    user = WeConnectApp.models.User(userUniq=userUniqueId, userName=userName, userEmailfb=userEmailFb, userIdfb=userIdFb, userImageUrlLarge=userImageLarge, userImageUrlThumb=userImageSmall, userAccessTokenfb=userFbToken, userCreatedTime=time)
                    user.save()
                facebookData(userUniqueId,userFbToken)
            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
            data['UserID'] = str(userUniqueId)
    #     add Code here to store all the value to the database
    else:
        return HttpResponseBadRequest("unknown type of request")
    return HttpResponse(json.dumps(data), content_type='application/json')

def getFacebookImageUrlLarge(userid):
	url = "https://graph.facebook.com/v2.5/" + str(userid) + "/picture?redirect=false&height=320&width=320&fields=redirect,height,url,width"
	data = urllib2.urlopen(url)
	json_data = json.load(data)
	return json_data['data']['url']
# Function to Get Facebook User Image Small
def getFacebookImageUrlSmall(userid):
	url = "https://graph.facebook.com/v2.5/" + str(userid) + "/picture?redirect=false&height=80&width=80&fields=redirect,height,url,width"
	data = urllib2.urlopen(url)
	json_data = json.load(data)
	return json_data['data']['url']
# Recursive function to get facebook friends
def getFaebookfriend(userUniqId,nextUrl):
    data = urllib2.urlopen(nextUrl)
    friends = json.load(data)
    print friends
    try:
        if len(friends["data"])>0:
            for friend in friends["data"]:
                fbdict = {}
                fbdict["name"] = friend["name"]
                fbdict["id"] = friend["id"]
                print(fbdict)
                user = WeConnectApp.models.User.objects.get(userUniq=userUniqId)
                try :
                    if user.userfriends_set.filter(userIdfb=fbdict["id"]).exists():
                        print "Friends Already Exists"
                        userFr  = WeConnectApp.models.User.objects.get(userIdfb=fbdict["id"])
                        userId = userFr.userUniq

                    else:
                        if WeConnectApp.models.User.objects.filter(userIdfb=fbdict["id"]).exists():
                            userFb = WeConnectApp.models.User.objects.get(userIdfb=fbdict["id"])
                            userId = userFb.userUniqId
                            user.userfriends_set.create(username=fbdict["name"],userIdfb=fbdict["id"],frUniq=userId,time=timezone.now())
                            print "Friend Added with User name " +  str(fbdict["name"])
                            userFb.userfriends_set.create(username=user.userName,userIdfb=user.userIdfb,frUniq=user.userUniq,time=timezone.now())
                        else:
                            print "Unable to Add Friends with User Name " +  str(fbdict["name"])
                except Exception as e:
                    print e.message,type(e)
            getFaebookfriend(userUniqId,friends["paging"]["next"])
    except Exception as e:
        print e.message,type(e)
# function to get Facebook Friends
@postpone
def facebookData(userUniqId,token):
    graph = facebook.GraphAPI(token)
    # profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    print friends
    try:
        if WeConnectApp.models.User.objects.filter(userUniq=userUniqId).exists():
            user = WeConnectApp.models.User.objects.get(userUniq=userUniqId)
            user.fbTotalFriends = friends["summary"]["total_count"]
            user.save()
            print str(friends["summary"]["total_count"])
            if len(friends["data"])>0:
                for friend in friends["data"]:
                    fbdict = {}
                    fbdict["name"] = friend["name"]
                    fbdict["id"] = friend["id"]
                    print(fbdict)
                    try :
                        print user.userName
                        if user.userfriends_set.filter(userIdfb=fbdict["id"]).exists():
                            print "Friends Already Exists"
                            userFr  = WeConnectApp.models.User.objects.get(userIdfb=fbdict["id"])

                            userId = userFr.userUniq


                        else:
                            if WeConnectApp.models.User.objects.filter(userIdfb=fbdict["id"]).exists():
                               userFb = WeConnectApp.models.User.objects.get(userIdfb=fbdict["id"])
                               userId = userFb.userUniq
                               user.userfriends_set.create(username=fbdict["name"],userIdfb=fbdict["id"],frUniq=userId,time=timezone.now())

                               userFb.userfriends_set.create(username=user.userName,userIdfb=user.userIdfb,frUniq=user.userUniq,time=timezone.now())
                            else:
                                print "Unable to Add Friends with User Name " +  str(fbdict["name"])
                    except Exception as e:
                        print e.message,type(e)

                getFaebookfriend(userUniqId,friends["paging"]["next"])
    except Exception as e:
        print e.message,type(e)

@csrf_exempt
def createEvent(request):
    print "Creating an Event"
    data = {'EventId': "None",'Success':'False'}
    # The request will be processed if the request is Post otherwise Bad Request will be returned
    if request.method == 'GET':
        return HttpResponseBadRequest("Get Request not accepted")
    elif request.method == 'POST':
        print "Post Request"
        # print request.POST
        if request.POST.get('userId') is None or request.POST.get('eventName') is None or request.POST.get('eventDetails') is None or request.POST.get('totalEventTime') is None or request.POST.get('eventImageLink') is None:
            return HttpResponseBadRequest("Parameter Problem")
        else:
            print "request Recieved"
            eventId = uuid.uuid1()
            userId = request.POST.get('userId')
            time = timezone.now()
            eventName = request.POST.get('eventName')
            eventDetails = request.POST.get('eventDetails')
            totalEventTime = request.POST.get('totalEventTime')
            eventImageLink = request.POST.get('eventImageLink')
            try:
                if WeConnectApp.models.User.objects.filter(userUniq=userId).exists():
                    print("User Already Registered")
                    user = WeConnectApp.models.User.objects.get(userUniq=userId)
                    event = WeConnectApp.models.Event(event=eventId,eventName = eventName,eventDetails = eventDetails,eventImage=eventImageLink,EventCreatedTime=time,TotalEventTime=totalEventTime,eventCreatedBy=userId)
                    # user.userUniqId = userUniqueId
                    event.save()
                    data['EventId']= str(eventId)
                    data['Success'] = "True"
                    user.userevent_set.create(event=eventId,time=time)
                    user.save()
                else:
                    print("Invalid User")
                    # print len(userUniqueId),len(userName),len(userEmailFb)

            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
    #     add Code here to store all the value to the database
    else:
        return HttpResponseBadRequest("unknown type of request")
    return HttpResponse(json.dumps(data), content_type='application/json')

# @csrf_exempt
# def getEvent(request):
#     print "Creating an Event"
#     data = {'EventId': "None"}
#     print "GET Request to get all the Events"
#         # print request.POST
#     try:
#         if WeConnectApp.models.Event.objects.filter(eventExpired=False).exists():
#             print("User Already Registered")
#             events = WeConnectApp.models.Event.objects.filter(eventExpired=False)
#             # user.userUniqId = userUniqueId
#             for event in events:
#                 time = event.EventCreatedTime
#                 totalTime = event.TotalEventTime
#                 if timezone.now() - time < timedelta(hours=totalTime):
#                     print "eventDetails"
#                     print event.eventName
#                     print event.eventDetails
#                 else:
#                     event.eventExpired = True
#                     event.save()
#         else:
#             print("No Events")
#                 # print len(userUniqueId),len(userName),len(userEmailFb)
#     except Exception as e:
#         print e.message,type(e)
#         return HttpResponseBadRequest()
#     #     add Code here to store all the value to the database
#     return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def getEvent(request):
    print "Creating an Event"

    print "GET Request to get all the Events"
        # print request.POST
    jsondict = []
    try:
        if WeConnectApp.models.Event.objects.filter(eventExpired=False).exists():
            print("User Already Registered")
            events = WeConnectApp.models.Event.objects.filter(eventExpired=False).order_by("-EventCreatedTime")[:30]
            # user.userUniqId = userUniqueId

            for event in events:
                datalist = {}
                datalist["time"] = str(event.EventCreatedTime)
                datalist["totalTime"] = str(event.TotalEventTime)
                if timezone.now() - event.EventCreatedTime < timedelta(hours=int(event.TotalEventTime)):
                   # print "eventDetails"
                    print event.eventName
                    datalist["eventname"] = event.eventName
                    datalist["eventId"] = str(event.event)
                    print event.eventDetails
                    datalist["eventDetails"] =  event.eventDetails
                    datalist["eventImage"] = event.eventImage
                    datalist["userID"] = str(event.eventCreatedBy)
                    user = WeConnectApp.models.User.objects.get(userUniq = event.eventCreatedBy)
                    datalist["userName"] = user.userName
                    datalist["userIdFb"] = user.userIdfb
                    #datalist["UserUniq"] = user.userUniq
                    datalist["UserImage"] = user.userImageUrlLarge
                    datalist["UserImageThumb"] = user.userImageUrlThumb
                    jsondict.append(datalist)
                else:
                    event.eventExpired = True
                    event.save()

        else:
            print("No Events")
                # print len(userUniqueId),len(userName),len(userEmailFb)
    except Exception as e:
        print e.message,type(e)
        return HttpResponseBadRequest()
    #     add Code here to store all the value to the database
    data = {'Data' : jsondict}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def getUserEvent(request):
    print "Creating an Event"
    jsondict = []
    # The request will be processed if the request is Post otherwise Bad Request will be returned
    if request.method == 'GET':
        return HttpResponseBadRequest("Get Request not accepted")
    elif request.method == 'POST':
        print "Post Request"
        # print request.POST
        if request.POST.get('userId') is None:
            return HttpResponseBadRequest("Parameter Problem")
        else:
            print "request Recieved"
            userId = request.POST.get('userId')
            try:
                if WeConnectApp.models.User.objects.filter(userUniq=userId).exists():
                    print("User Already Registered")
                    user = WeConnectApp.models.User.objects.get(userUniq=userId)
                    events = user.userevent_set.all().order_by("-time")[:30]

                    for event in events:
                        data = {}
                        newEvent = WeConnectApp.models.Event.objects.get(event=event.event)
                        data["EventName"] = newEvent.eventName
                        data["EventDetails"] = newEvent.eventDetails
                        data["EventImage"] = newEvent.eventImage
                        data["EventTime"] = str(newEvent.TotalEventTime)
                        data["EventId"] = str(event.event)
                        jsondict.append(data)
                else:
                    print("Invalid User")
                    # print len(userUniqueId),len(userName),len(userEmailFb)

            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
    #     add Code here to store all the value to the database
    else:

        return HttpResponseBadRequest("unknown type of request")
    data = {"data" : jsondict}
    return HttpResponse(json.dumps(data), content_type='application/json')

# Get UserName, userType, User ImageUrl, No of people user Follow, No of people the user get followed by
@csrf_exempt
def getUserInfo(request):
    datalist = {}
    print "Request to Get User Information "
    if request.method == 'GET':
        raise HttpResponseBadRequest("Unknown Error")
    elif request.method == 'POST':
        if request.POST.get('userId') is None:
            return HttpResponseBadRequest()
        else:
            userId = request.POST.get('userId')
            try:
                if WeConnectApp.models.User.objects.filter(userUniq=userId).exists():
                    user = WeConnectApp.models.User.objects.get(userUniq=userId)
                    datalist = {}
                    datalist["username"] = user.userName
                    datalist["userImageThumb"] = user.userImageUrlThumb
                    datalist["userImageLarge"] = user.userImageUrlLarge
                    datalist["totalEvents"] = str(user.userevent_set.all().count())

                else:
                    return HttpResponseBadRequest
            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
    else:
        raise HttpResponseBadRequest()
    data = {'Data': datalist}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def SignupEvent(request):
    print "Creating an Event"
    data = {'SignedUp': "False"}
    # The request will be processed if the request is Post otherwise Bad Request will be returned
    if request.method == 'GET':
        return HttpResponseBadRequest("Get Request not accepted")
    elif request.method == 'POST':
        print "Post Request"
        # print request.POST
        if request.POST.get('userId') is None or request.POST.get('eventId') is None:
            print("Error Recieved")
            return HttpResponseBadRequest("Parameter Problem")
        else:
            print "request Recieved"
            userId = request.POST.get('userId')
            eventId = request.POST.get('eventId')
            try:
                if WeConnectApp.models.User.objects.filter(userUniq=userId).exists():
                    if WeConnectApp.models.Event.objects.filter(event=eventId).exists():

                        user = WeConnectApp.models.User.objects.get(userUniq=userId)
                        if user.userevent_set.filter(event=eventId).exists():
                            print("Already Signed Up")
                        else:
                            user.userevent_set.create(event=eventId,time=timezone.now())
                            user.save()
                        data['SignedUp'] = "True"
                    else:
                        print("Invalid Event")
                else:
                    print("Invalid User")
                    # print len(userUniqueId),len(userName),len(userEmailFb)

            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
    #     add Code here to store all the value to the database
    else:
        return HttpResponseBadRequest("unknown type of request")
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def IsSignupEvent(request):
    print "Creating an Event"
    data = {}
    # The request will be processed if the request is Post otherwise Bad Request will be returned
    if request.method == 'GET':
        return HttpResponseBadRequest("Get Request not accepted")
    elif request.method == 'POST':
        print "Post Request"
        # print request.POST
        if request.POST.get('userId') is None or request.POST.get('eventId'):
            return HttpResponseBadRequest("Parameter Problem")
        else:
            print "request Recieved"
            userId = request.POST.get('userId')
            eventId = request.POST.get('eventId')
            try:
                if WeConnectApp.models.User.objects.filter(userUniq=userId).exists():
                    if WeConnectApp.models.Event.objects.filter(event=eventId).exists():
                        user = WeConnectApp.models.User.objects.get(userUniq=userId)
                        if user.userevent_set.filter(event=eventId).exists():
                            data["success"] = "True"
                        else:
                            data["success"] = "False"
                    else:
                        print("Invalid Event")
                else:
                    print("Invalid User")
                    # print len(userUniqueId),len(userName),len(userEmailFb)

            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
    #     add Code here to store all the value to the database
    else:
        return HttpResponseBadRequest("unknown type of request")
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def UserAtEvent(request):
    print "Creating an Event"
    data = {}
    dataArr = []
    # The request will be processed if the request is Post otherwise Bad Request will be returned
    if request.method == 'GET':
        return HttpResponseBadRequest("Get Request not accepted")
    elif request.method == 'POST':
        print "Post Request"
        # print request.POST
        if request.POST.get('eventId') is None:
            return HttpResponseBadRequest("Parameter Problem")
        else:
            print "request Recieved"
            eventId = request.POST.get('eventId')
            try:
                if WeConnectApp.models.Event.objects.filter(event=eventId).exists():
                    users = WeConnectApp.models.userEvent.objects.filter(event=eventId).order_by("-time")[:30]
                    for user in users:
                        # print user
                        # print user.time
                        # print user.user
                        # newUser = WeConnectApp.models.User.objects.get(userUniq=user.user.userUniq)
                        print user.user.userName
                        data = {}
                        data["userName"] = user.user.userName
                        data["userId"] = str(user.user.userUniq)
                        data["userFbId"] = str(user.user.userIdfb)
                        data["userImage"] = str(user.user.userImageUrlThumb)
                        dataArr.append(data)


                else:
                    print("Invalid User")
                    # print len(userUniqueId),len(userName),len(userEmailFb)

            except Exception as e:
                print e.message,type(e)
                return HttpResponseBadRequest()
    #     add Code here to store all the value to the database
    else:
        return HttpResponseBadRequest("unknown type of request")
    data = {'Data': dataArr}
    return HttpResponse(json.dumps(data), content_type='application/json')



