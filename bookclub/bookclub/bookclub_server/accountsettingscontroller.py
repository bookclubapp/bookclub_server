import hashlib

from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import json
from .models import User, Match, TradeList, Suggestion, WishList, Book, AccountSettings
from django.http import JsonResponse
from django.db.models import Q
import random


@api_view(['GET'])
def index(request):
    if "user" in request.session:
        status = "success"
        message = "here is the account info"
        account_info = AccountSettings.objects.get(user_id=request.session['user'])
    else:
        status = "error"
        message = "you should login first"
        json_data = {"status": status, "message": message, "account_settings": None}

    json_data = {"status": status, "message": message, "account_settings": model_to_dict(account_info)}
    return JsonResponse(json_data, safe=False)


@api_view(['GET'])
def reset(request):
    if "user" in request.session:
        status = "success"
        message = "account settings were reset succesfully"
        account_info = AccountSettings.objects.get(user_id=request.session['user'])
        account_info.userAvailability = True
        account_info.userMessagable = True
        account_info.lastSeen = True
        account_info.save()
        json_data = {"status": status, "message": message, "account_settings": model_to_dict(account_info)}
    else:
        status = "error"
        message = "you should login first"
        json_data = {"status": status, "message": message, "account_settings": None}

    return JsonResponse(json_data, safe=False)


@api_view(['GET'])
def change_user_availability(request):
    if "user" in request.session:
        status = "success"
        message = "user availability was changed succesfully"
        account_info = AccountSettings.objects.get(user_id=request.session['user'])
        if account_info.userAvailability:
            account_info.userAvailability = False
        else:
            account_info.userAvailability = True
        account_info.save()
        json_data = {"status": status, "message": message, "account_settings": model_to_dict(account_info)}
    else:
        status = "error"
        message = "you should login first"
        json_data = {"status": status, "message": message, "account_settings": None}

    return JsonResponse(json_data, safe=False)


@api_view(['GET'])
def change_user_messagable(request):
    if "user" in request.session:
        status = "success"
        message = "user messagable was changed succesfully"
        account_info = AccountSettings.objects.get(user_id=request.session['user'])
        if account_info.userMessagable:
            account_info.userMessagable = False
        else:
            account_info.userMessagable = True
        account_info.save()
        json_data = {"status": status, "message": message, "account_settings": model_to_dict(account_info)}
    else:
        status = "error"
        message = "you should login first"
        json_data = {"status": status, "message": message, "account_settings": None}

    return JsonResponse(json_data, safe=False)


@api_view(['GET'])
def change_last_seen_state(request):
    if "user" in request.session:
        status = "success"
        message = "last seen state was changed succesfully"
        account_info = AccountSettings.objects.get(user_id=request.session['user'])
        if account_info.lastSeen:
            account_info.lastSeen = False
        else:
            account_info.lastSeen = True
        account_info.save()
        json_data = {"status": status, "message": message, "account_settings": model_to_dict(account_info)}
    else:
        status = "error"
        message = "you should login first"
        json_data = {"status": status, "message": message, "account_settings": None}

    return JsonResponse(json_data, safe=False)


@api_view(['GET'])
def change_online_state(request):
    if "user" in request.session:
        user = User.objects.get(id=request.session['user'])
        if user.onlineState:
            user.onlineState = False
        else:
            user.onlineState = True
        user.save() # will use the real picture to store
        status = 'success'
        message = 'the user\'s online state was updated successfully'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def change_profile_picture(request):
    user_data = json.loads(request.body)  # {"profile_picture":"something.jpg"}
    if "user" in request.session:
        user = User.objects.get(id=request.session['user'])
        user.profilePicture = user_data['profile_picture']
        user.save() # will use the real picture to store
        status = 'success'
        message = 'the profile picture was updated successfully'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def change_phone_number(request):
    user_data = json.loads(request.body)  # {"phone_number":"5318316467
    if "user" in request.session:
        user = User.objects.get(id=request.session['user'])
        user.phoneNumber = user_data['phone_number']
        user.save()  # will use the real picture to store
        status = 'success'
        message = 'the phone number was updated successfully'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def change_location(request):
    user_data = json.loads(request.body)  # {"long":"0.0000", "lat":"0.0000", "country":"Turkey"}
    if "user" in request.session:
        user = User.objects.get(id=request.session['user'])
        user.long = user_data['long']
        user.lat = user_data['lat']
        user.country = user_data['country']
        user.save()  # will use the real picture to store
        status = 'success'
        message = 'the user\'s location was updated successfully'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def change_email(request):
    # gps will be added (discussed)
    user_data = json.loads(request.body)  # {"mail":"something@gmail.com"}
    if "user" in request.session:
        user = User.objects.get(id=request.session['user'])
        user.mail = user_data['mail']
        user.save()  # will use the real picture to store
        status = 'success'
        message = 'the email address was updated successfully'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def change_password(request):
    user_data = json.loads(request.body)  # {"password":"acacac"}
    if "user" in request.session:
        user = User.objects.get(id=request.session['user'])
        salt = "%7hYY+5"
        to_be_hashed = user_data["password"] + salt
        hashed = hashlib.md5(to_be_hashed.encode('utf8')).hexdigest()
        user.password = hashed
        user.save()  # will use the real picture to store
        status = 'success'
        message = 'the password was updated successfully'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)