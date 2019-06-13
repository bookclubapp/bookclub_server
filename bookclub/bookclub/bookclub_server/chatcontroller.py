from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.utils import json
from .models import User, Chat, Message
from django.http import JsonResponse
from django.db.models import Q


@api_view(['GET'])
def index(request): # WORKS
    # does not need any json loading
    # returns whatsapp chat list
    if "user" in request.session:
        chat = Chat.objects.filter(Q(user_id_2=request.session['user']) | Q(user_id_1=request.session['user']))
        if chat.exists():
            chat_list = []
            # i dont think we should limit it here for now
            for line in chat:
                chat_list.append(model_to_dict(line))
            status = 'success'
            message = 'chat data sent successfully'
        else:
            status = 'error'
            message = 'no chat data for this user'
            chat_list = None
    else:
        status = 'error'
        message = 'you should login first'
        chat_list = None

    json_data = {"status": status, "message": message, "chat_info": chat_list}
    return JsonResponse(json_data)