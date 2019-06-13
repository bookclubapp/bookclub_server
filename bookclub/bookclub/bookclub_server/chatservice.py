from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.utils import json
from .models import User, Chat, Message
from django.http import JsonResponse
import datetime
from django.db.models import Q


@api_view(['POST'])
def send(request): # WORKS
    user_data = json.loads(request.body)  # {"messageText": "selam", "chat_id": "3"}
    if "user" in request.session:
        if Chat.objects.filter(Q(id=user_data['chat_id'])).exists():
            row = Chat.objects.get(id=user_data['chat_id'])
            if row.user_id_1_id == request.session['user'] or row.user_id_2_id == request.session['user']:
                message = Message(messageText=user_data['messageText'], messageDate=datetime.datetime.now(), isSeen=0,
                                  chat_id=Chat.objects.get(id=user_data['chat_id']),
                                  sender_id=User.objects.get(id=request.session['user']))
                message.save()
                status = 'success'
                message = 'Message successfully sent'
            else:
                status = 'error'
                message = 'You cannot send messages in this chat'
        else:
            status = 'error'
            message = 'There is no such chat'
    else:
        status = 'error'
        message = 'You should login first'
    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def message_list(request): # WORKS
    chat_data = json.loads(request.body)  # {"chat_id":"1"}
    if "user" in request.session:
        messages = Message.objects.filter(chat_id=chat_data['chat_id'])
        if messages.exists():
            message_list = []
            for line in messages:
                message_list.append({
                    "date_info": line.messageDate,
                    "isSeen_info": line.isSeen,
                    "text_info": line.messageText,
                    "sender_info": line.sender_id.id
                })
            status = 'success'
            message = 'message data sent successfully'
        else:
            status = 'error'
            message = 'there is no message data with this id'
            message_list = None
    else:
        status = "error"
        message = "you should login first"
        message_list = None

    json_data = {"status": status, "message": message, "message_info": message_list}
    return JsonResponse(json_data)


@api_view(['POST'])
def read(request): # WORKS
    message_data = json.loads(request.body)  # {"message_id":"1"}
    if "user" in request.session:
        message = Message.objects.filter(id=message_data['message_id'])
        if message.exists():
            message.update(isSeen=1)
            status = 'success'
            message = 'message status changed'
        else:
            status = 'error'
            message = 'no message with this id'
    else:
        status = "error"
        message = "you should login first"

    json_data = {"status": status,
                 "message": message
                 }
    return JsonResponse(json_data)