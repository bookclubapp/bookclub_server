from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.utils import json
from .models import User, History,Match,Book
from django.http import JsonResponse


@api_view(['GET'])
def index_match(request): # WORKS
    if "user" in request.session:
        history = History.objects.filter(user_id=request.session['user'])
        if history.exists():
            history_list = []
            index = 0 
            for line in history:
                index += 1
                if not line.match_id== None :
                    givingbook = Book.objects.get(id=line.match_id.giving_book_id)
                    wantedbook = Book.objects.get(id=line.match_id.wanted_book_id)
                    history_list.append({"match_history_info": model_to_dict(line),
                                            "match_info": model_to_dict(line.match_id),
                                            "giving_book_info" : model_to_dict(givingbook),
                                            "wanted_book_info": model_to_dict(wantedbook),
                                            })
                if index > 50:
                    break
            status = 'success'
            message = 'history data send successfully'
        else:
            status = 'error'
            message = 'no history for this user'
            history_list = None
    else:
        status = 'error'
        message = 'there is no user in the session'
        history_list = None
    json_data = {"status": status,
                 "message": message,
                 "history": history_list,
                 }
    return JsonResponse(json_data)

@api_view(['GET'])
def index_suggestion(request): # WORKS
    if "user" in request.session:
        history = History.objects.filter(user_id=request.session['user'])
        if history.exists():
            history_list = []
            index = 0
            for line in history:
                index += 1
                if not line.suggestion_id == None :
                    givingbook = Book.objects.get(id=line.suggestion_id.giving_book_id)
                    wantedbook = Book.objects.get(id=line.suggestion_id.wanted_book_id)
                    history_list.append({"suggestion_history_info": model_to_dict(line),
                                            "suggestion_info": model_to_dict(line.suggestion_id),
                                             "giving_book_info": model_to_dict(givingbook),
                                            "wanted_book_info": model_to_dict(wantedbook),
                                            })
                if index > 50:
                    break
            status = 'success'
            message = 'history data send successfully'
        else:
            status = 'error'
            message = 'no history for this user'
            history_list = None
    else:
        status = 'error'
        message = 'there is no user in the session'
        history_list = None
    json_data = {"status": status,
                 "message": message,
                 "history": history_list,
                 }
    return JsonResponse(json_data)

@api_view(['GET'])
def clear(request): # WORKS
    if "user" in request.session:
        history = History.objects.filter(user_id=request.session['user'])
        if history.exists():
            for item in history:
                item.delete()
            status = 'success'
            message = 'history data deleted successfully'
        else:
            status = 'error'
            message = 'no history for this user'
    else:
        status = 'error'
        message = 'there is no user in the session'
    json_data = {"status": status,
                 "message": message
                 }
    return JsonResponse(json_data)