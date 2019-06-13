from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.utils import json
from .models import User, Chat, Message
from django.http import JsonResponse
from django.db.models import Q


@api_view(['POST'])
def index(request):
    user_data = json.loads(request.body) # {"message_id":"1"} returns all info about one particular message
    message = Message.objects.get(Q(id=user_data['message_id']))
    if message:
        message_info= []
        message_info.append(model_to_dict(message))
        status = 'success'
        message = 'message data sent successfully'
    else:
        status = 'error'
        message = 'there is no message data with this id'
        message_info = None

    json_data = {"status": status, "message": message, "message_info": message_info}
    return JsonResponse(json_data)