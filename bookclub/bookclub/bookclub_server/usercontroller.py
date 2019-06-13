from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import json
from .models import User, Match, TradeList, Suggestion, History, AccountSettings, UserRating, Chat, Book, WishList
from . import emailservice
from . import algorithm
from django.http import JsonResponse
from django.db.models import Q
import random
import datetime
import csv
from faker import Faker
from faker import Factory
import factory
import factory.django
import time
import hashlib

   
@api_view(['GET'])
def get_session(request): # WORKS
    # this method returns the id of the user who is in the session, 
    # if there is no user in the session it returns -1
    current_milli_time = int(round(time.time() * 1000))
    if "user" in request.session:
        enson = int(round(time.time() * 1000))
        return JsonResponse({'session_id': model_to_dict(User.objects.get(id=request.session['user'])),
                             'time':str(enson-current_milli_time)})
    else:
        return JsonResponse({'session_id': -1})


@api_view(['POST'])
def login(request): # WORKS
    # this method logs in the user whose cridentials are correct and opens up a new session
    # the session is not closed until the user logs out
    user_data = json.loads(request.body)
    if User.objects.filter(username=user_data['username']).exists():
        user = User.objects.get(username=user_data['username'])
        salt = "%7hYY+5"
        to_be_hashed = user_data['password'] + salt
        hashed = hashlib.md5(to_be_hashed.encode('utf8')).hexdigest()
        if user.password == hashed:
            status = 'success'
            message = 'you are logged in'
            user.onlineState = 1
            user.save()
            request.session['user'] = user.id # opened a session
        else:
            status = 'error'
            message = 'the password is incorrect'
    else:
        status = 'error'
        message = 'there is no user with this username'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def signup(request): # WORKS
    # this method signs up the user and opens a session for them
    # it also adds the user's account settings into the accountsettings table
    user_data = json.loads(request.body)
    if User.objects.filter(username=user_data['username']).exists() or User.objects.filter(mail=user_data['mail']).exists():
        status = 'error'
        message = 'This username or email address already exists'
    else:
        status = 'success'
        message = 'User successfully signed up'
        salt = "%7hYY+5"
        to_be_hashed = user_data['password'] + salt
        user = User(name=user_data['name'], country=user_data['country'],
                    mail=user_data['mail'], phoneNumber=user_data['phoneNumber'], dateOfBirth=user_data['dateOfBirth'],
                    username=user_data['username'], password=hashlib.md5(to_be_hashed.encode('utf8')).hexdigest(), long=user_data['long'],
                    lat=user_data['lat'], onlineState=1,
                    profilePicture=user_data['profilePicture'])
        user.save()
        user_settings = AccountSettings(user_id=user)
        user_settings.save()
        request.session['user'] = user.id # opened a session
        emailservice.signup_email(request) # signup mail is sent

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def forgot_password(request): # WORKS
    # this method is for resetting the password if it is forgotten
    data = json.loads(request.body)
    user_row = User.objects.filter((Q(username=data['username']) | Q(mail=data['mail'])))
    # if data['mail'] == user.mail:
    if user_row.exists():
        for user in user_row:
            status = 'success'
            message = 'new password will be sent'
            s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?."
            p = "".join(random.sample(s, 8))
            new_password = p
            new_request = {"username": user.username, "mail": user.mail, "new_password": new_password}
            emailservice.forgot_password_email(json.dumps(new_request))
            salt = "%7hYY+5"
            to_be_hashed = new_password + salt
            hashed = hashlib.md5(to_be_hashed.encode('utf8')).hexdigest()
            user.password = hashed
            user.save()
    else:
        status = 'error'
        message = 'user does not exist'
        new_password = -1

    json_data = {"status": status, "message": message, "password": new_password}
    return JsonResponse(json_data)


@api_view(['GET'])
def sign_out(request): # WORKS
    # this method signs out the user and closes session
    if "user" in request.session:
        user = User.objects.get(id=request.session["user"])
        user.onlineState = 0
        user.save()
        del request.session['user'] # session is closed
        status = 'success'
        message = 'you signed out'
    else:
        status = 'error'
        message = 'there is no user in the session'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def see_other_user_profile(request): # WORKS
    # returns the profile of a user
    data = json.loads(request.body)
    if User.objects.filter(username=data['username']).exists():
        user = User.objects.get(username=data['username'])
        status = 'success'
        message = 'other user data send successfully'
        json_data = {"status": status, "message": message, "user_info": model_to_dict(user)}
    else:
        status = 'error'
        message = 'there is no user with this name'
        json_data = {"status": status, "message": message}

    return JsonResponse(json_data)


@api_view(['POST'])
def get_user_rating(request):
    user_data = json.loads(request.body)
    userRatings = UserRating.objects.filter(rated_user_id= user_data['id'])
    if userRatings.exists():
        rate_sum = 0
        for rates in userRatings:
            rate_sum = rate_sum + rates.rating
        if len(userRatings) == 0:
            final_rate = 2.5
        else:
            final_rate = rate_sum / len(userRatings)
        status = 'success'
        message = 'user rating send successfully'
    else:
        status = 'error'
        message = 'there is no user with this id'
        final_rate= None
    json_data = {"status": status, "message": message, "final_rate": str(final_rate)}
    return JsonResponse(json_data)
    

@api_view(['POST'])
def get_user_profile_id(request):
    # returns the profile of a user with given id
    data = json.loads(request.body)
    if User.objects.filter(id=data['user_id']).exists():
        user = User.objects.get(id=data['user_id'])
        status = 'success'
        message = 'other user data send successfully'
        json_data = {"status": status, "message": message, "user_info": model_to_dict(user)}
    else:
        status = 'error'
        message = 'there is no user with this name'
        json_data = {"status": status, "message": message}

    return JsonResponse(json_data)


@api_view(['GET'])
def get_user_profile(request): # WORKS
    # returns the profile of a user in the session
    if "user" in request.session:
        status = 'success'
        message = 'other user data send successfully'
        user = User.objects.get(id=request.session['user'])
        json_data = {"status": status, "message": message, "user_info": model_to_dict(user)}
    else:
        status = 'error'
        message = 'there is no user with this name'
        json_data = {"status": status, "message": message}

    return JsonResponse(json_data)


@api_view(['GET'])
def match_list_index(request): # WORKS
    # does not need any json loading because checking with session already

    if "user" in request.session:
        matchlistIndex = []
        matchlistRows = Match.objects.filter(Q(user_id=request.session['user']) & Q(state='pending')).order_by('-match_score')
        if matchlistRows.exists():
            status = 'success'
            message = 'Match list will be displayed'
            index = 0
            for match in matchlistRows:
                index += 1
                matchlistIndex.append({"matchlist_info": model_to_dict(match),
                                       "givingBook_info": model_to_dict(match.giving_book),
                                       "wantedBook_info": model_to_dict(match.wanted_book)})
                if index > 50: # limited for 50 matches only - no randomizing
                    break
        else:
            status = "error"
            message = "there is no match list to display"
            matchlistIndex = None
    else:
        status = 'error'
        message = 'you should login first'
        matchlistIndex = None
    json_data = {"status": status, "message": message, "matchlistIndex": matchlistIndex}
    return JsonResponse(json_data)


@api_view(['GET'])
def suggestion_list_index(request): # WORKS
    # does not need any json loading
    if "user" in request.session:
        suggests = Suggestion.objects.filter(user_id=request.session['user']).order_by('-recommendation_score')
        if suggests.exists():
            suggest_list = []
            index = 0
            for suggest in suggests:
                index += 1
                suggest_list.append({
                    "suggest_info": model_to_dict(suggest),
                    "giving_book_info": model_to_dict(suggest.giving_book),
                    "wanted_book_info": model_to_dict(suggest.wanted_book),
                    "suggested_book_info": model_to_dict(suggest.suggested_book_id)
                })
                if index > 50: # limited for 50 suggestions only - no randomizing
                    break
            status = 'success'
            message = 'suggestion data sent successfully'
        else:
            status = 'error'
            message = 'no suggestion for this user'
            suggest_list = None
    else:
        status = 'error'
        message = 'you should login first'
        suggest_list = None

    json_data = {"status": status, "message": message, "suggestionList": suggest_list}
    return JsonResponse(json_data)


@api_view(['GET'])
def main_menu_index(request): # WORKS
    # this function returns the books from the menu screen of the user
    # user_data = json.loads(request.body) # json = { "action":"main_menu" } it is optional is not needed actually
    # if there is a user in the session
    menu_index = []
    if "user" in request.session:
        tradelist = TradeList.objects.filter(~Q(user_id=request.session['user']))
        if tradelist.exists():
            status = "success"
            message = "here are the books for your main menu"
        else:
            status = "error"
            message = "there is nothing to show for the main menu"
            menu_index = None
    else:
        tradelist = TradeList.objects.all()
        if tradelist.exists():
            status = "success"
            message = "here are the books for your main menu"
        else:
            status = "error"
            message = "there is nothing to show for the main menu"
            menu_index = None
    index = 0
    for trade in tradelist:
        index += 1
        menu_index.append({
            "trade_info": model_to_dict(trade),
            "book_info": model_to_dict(trade.givingBook_id),
            "user_info": model_to_dict(trade.user_id)
        })
        if index > 50:
            break

    json_data = {"status": status, "message": message, "mainMenuIndex": menu_index}
    return JsonResponse(json_data, safe=False)


@api_view(['POST'])
def search_index(request): # WORKS
    user_data = json.loads(request.body)  # json = { "search_query":"something" }
    search_index = []
    if "user" in request.session:
        tradelist = TradeList.objects.filter(~Q(user_id=request.session['user'])).select_related(
            "givingBook_id").filter(givingBook_id__title__icontains=user_data['search_query'])
        if tradelist.exists():
            status = "success"
            message = "the search query is found successfully"
        else:
            status = "error"
            message = "nothing was found for this search query"
            search_index = None
    else:
        tradelist = TradeList.objects.all().select_related("givingBook_id").filter(
            givingBook_id__title__icontains=user_data['search_query'])
        if tradelist.exists():
            status = "success"
            message = "the search query is found successfully"
        else:
            status = "error"
            message = "nothing was found for this search query"
            search_index = None

    index = 0
    for trade in tradelist:
        index += 1
        search_index.append({
            "trade_info": model_to_dict(trade),
            "book_info": model_to_dict(trade.givingBook_id),
            "user_info": model_to_dict(trade.user_id)
        })
        if index > 50:
            break

    json_data = {"status": status, "message": message, "searchIndex": search_index}
    return JsonResponse(json_data, safe=False)


@api_view(['POST'])
def search_book(request): # WORKS
    user_data = json.loads(request.body)  # json = { "search_book":"something" }
    books_index = []
    books = Book.objects.filter(title__icontains=user_data['search_book'])
    if "user" in request.session:
        if books.exists():
            status = "success"
            message = "the booklist is found"
        else:
            status = "error"
            message = "there is no book"
            books_index = None
    index = 0
    for book in books:
        index += 1
        books_index.append({"book_info": model_to_dict(book)})
        if index > 50:
            break

    json_data = {"status": status, "message": message, "books_index": books_index}
    return JsonResponse(json_data, safe=False)


@api_view(['POST'])
def get_book(request): # WORKS
    data = json.loads(request.body)  # json = { "book_id":"2" }
    if Book.objects.filter(id=data['book_id']).exists():
        book = Book.objects.get(id=data['book_id'])
        status = 'success'
        message = 'book data send successfully'
        json_data = {"status": status, "message": message, "book_info": model_to_dict(book)}
    else:
        status = 'error'
        message = 'there is no book with this id'
        json_data = {"status": status, "message": message}

    return JsonResponse(json_data)


@api_view(['POST'])
def action_on_match(request): # WORKS
    # check if there is a user in the session
    if "user" in request.session:
        # load user data: {"match_id":1, "state":'confirmed'}
        user_data = json.loads(request.body)
        # find that match row in the match list
        match = Match.objects.filter(id=user_data['match_id'])
        # if there is such match
        if match.exists():
            match = Match.objects.get(id=user_data['match_id'])
            # check if the user in the session has a privilege for proceeding and action
            if match.user_id.id == request.session['user']:
                other_users_match = Match.objects.filter((Q(user_id=match.matched_user) & Q(matched_user=match.user_id)) & (Q(wanted_book=match.giving_book) & Q(giving_book=match.wanted_book)))
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                if other_users_match.exists():
                    other_users_match = Match.objects.get((Q(user_id=match.matched_user) & Q(matched_user=match.user_id)) & (Q(wanted_book=match.giving_book) & Q(giving_book=match.wanted_book)))
                    # if session user confirmed the match
                    if user_data['state'] == 'confirmed':
                        if other_users_match.state == 'confirmed':
                            if match.state == 'pending':
                                match.state = 'confirmed'
                                match.save()
                                new_history_row = History(id=None, user_id=match.user_id, match_id=match, suggestion_id=None, state='confirmed', dateOfAction=date)
                                new_history_row.save()
                                new_chat = Chat(id=None, state_1='not_confirmed', state_2='not_confirmed', user_id_1=match.user_id, user_id_2=match.matched_user, match_id=match, suggestion_id=None)
                                new_chat.save()
                                status = 'success'
                                message = 'the match was confirmed from both sides'
                            else:
                                status = 'error'
                                message = 'this match is not active'
                        if other_users_match.state == 'rejected':
                            match.state = 'rejected'
                            match.save()
                            new_history_row = History(id=None, user_id=match.user_id, match_id=match, suggestion_id=None, state='rejected', dateOfAction=date)
                            new_history_row.save()
                            status = 'error'
                            message = 'the match could not be confirmed, because it was rejected by the other user'
                        if other_users_match.state == 'pending':
                            if match.state == 'pending':
                                match.state = 'confirmed'
                                match.save()
                                new_history_row = History(id=None, user_id=match.user_id, match_id=match, suggestion_id=None, state='confirmed', dateOfAction=date)
                                new_history_row.save()
                                status = 'success'
                                message = 'the match was confirmed'
                            else:
                                status = 'error'
                                message = 'this match is not active'
                    # if session user rejected the match
                    elif user_data['state'] == 'rejected':
                        match.state = 'rejected'
                        match.save()
                        other_users_match.state = 'rejected'
                        other_users_match.save()
                        new_history_row = History(id=None, user_id=match.user_id, match_id=match, suggestion_id=None, state='rejected', dateOfAction=date)
                        new_history_row.save()
                        status = 'success'
                        message = 'the match was rejected'
                else:
                    if user_data['state'] == 'confirmed':
                        if match.state == 'pending':
                            match.state = 'confirmed'
                            match.save()
                            new_history_row = History(id=None, user_id=match.user_id, match_id=match, suggestion_id=None, state='confirmed', dateOfAction=date)
                            new_history_row.save()
                            status = 'success'
                            message = 'the match was confirmed only by you for now'
                        else:
                            status = 'error'
                            message = 'this match is not active'
                    # if session user rejected the match
                    elif user_data['state'] == 'rejected':
                        if match.state == 'pending':
                            match.state = 'rejected'
                            match.save()
                            new_history_row = History(id=None, user_id=match.user_id, match_id=match, suggestion_id=None, state='rejected', dateOfAction=date)
                            new_history_row.save()
                            status = 'success'
                            message = 'the match was rejected'
                        else:
                            status = 'error'
                            message = 'this match is not active'
            else:
                status = 'error'
                message = 'you do not have a privilege to do this action'
        else:
            status = 'error'
            message = 'this match does not exist'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def action_on_suggestion(request): # WORKS
    # check if there is a user in the session
    if "user" in request.session:
        # load user data: {"suggestion_id":1, "state":'confirmed'}
        user_data = json.loads(request.body)
        # find that match row in the match list
        suggestion = Suggestion.objects.filter(id=user_data['suggestion_id'])
        # if there is such match
        if suggestion.exists():
            suggestion = Suggestion.objects.get(id=user_data['suggestion_id'])
            # check if the user in the session has a privilege for proceeding and action
            if suggestion.user_id.id == request.session['user']:
                other_users_suggestion = Suggestion.objects.filter((Q(user_id=suggestion.suggested_user) & Q(suggested_user=suggestion.user_id)) & (Q(suggested_book_id=suggestion.giving_book) & Q(giving_book=suggestion.suggested_book_id)))
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                if other_users_suggestion.exists():
                    other_users_suggestion = Suggestion.objects.get((Q(user_id=suggestion.suggested_user) & Q(suggested_user=suggestion.user_id)) & (Q(suggested_book_id=suggestion.giving_book) & Q(giving_book=suggestion.suggested_book_id)))
                    # if session user confirmed the match
                    if user_data['state'] == 'confirmed':
                        if other_users_suggestion.state == 'confirmed':
                            if suggestion.state == 'pending':
                                suggestion.state = 'confirmed'
                                suggestion.save()
                                new_history_row = History(id=None, user_id=suggestion.user_id, match_id=None, suggestion_id=suggestion, state='confirmed', dateOfAction=date)
                                new_history_row.save()
                                new_chat = Chat(id=None, state_1='not_confirmed', state_2='not_confirmed', user_id_1=suggestion.user_id, user_id_2=suggestion.suggested_user, match_id=None, suggestion_id=suggestion)
                                new_chat.save()
                                status = 'success'
                                message = 'the match was confirmed from both sides'
                            else:
                                status = 'error'
                                message = 'this match is not active'
                        if other_users_suggestion.state == 'rejected':
                            suggestion.state = 'rejected'
                            suggestion.save()
                            new_history_row = History(id=None, user_id=suggestion.user_id, match_id=None, suggestion_id=suggestion, state='rejected', dateOfAction=date)
                            new_history_row.save()
                            status = 'error'
                            message = 'the match could not be confirmed, because it was rejected by the other user'
                        if other_users_suggestion.state == 'pending':
                            if suggestion.state == 'pending':
                                suggestion.state = 'confirmed'
                                suggestion.save()
                                new_history_row = History(id=None, user_id=suggestion.user_id, match_id=None, suggestion_id=suggestion, state='confirmed', dateOfAction=date)
                                new_history_row.save()
                                status = 'success'
                                message = 'the match was confirmed'
                            else:
                                status = 'error'
                                message = 'this match is not active'
                    # if session user rejected the match
                    elif user_data['state'] == 'rejected':
                        suggestion.state = 'rejected'
                        suggestion.save()
                        other_users_suggestion.state = 'rejected'
                        other_users_suggestion.save()
                        new_history_row = History(id=None, user_id=suggestion.user_id, match_id=None, suggestion_id=suggestion, state='rejected', dateOfAction=date)
                        new_history_row.save()
                        status = 'success'
                        message = 'the match was rejected'
                else:
                    if user_data['state'] == 'confirmed':
                        if suggestion.state == 'pending':
                            suggestion.state = 'confirmed'
                            suggestion.save()
                            new_history_row = History(id=None, user_id=suggestion.user_id, match_id=None, suggestion_id=suggestion, state='confirmed', dateOfAction=date)
                            new_history_row.save()
                            status = 'success'
                            message = 'the match was confirmed only by you for now'
                        else:
                            status = 'error'
                            message = 'this match is not active'
                    # if session user rejected the match
                    elif user_data['state'] == 'rejected':
                        if suggestion.state == 'pending':
                            suggestion.state = 'rejected'
                            suggestion.save()
                            new_history_row = History(id=None, user_id=suggestion.user_id, match_id=None, suggestion_id=suggestion, state='rejected', dateOfAction=date)
                            new_history_row.save()
                            status = 'success'
                            message = 'the match was rejected'
                        else:
                            status = 'error'
                            message = 'this match is not active'
            else:
                status = 'error'
                message = 'you do not have a privilege to do this action'
        else:
            status = 'error'
            message = 'this match does not exist'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def confirm_trade(request): # WORKS
    user_data = json.loads(request.body)  # {"chat_id":"1", "state":"confirmed" or "state":"rejected"}
    # check if user is logged in
    if "user" in request.session:
        # if this chat exists
        chat = Chat.objects.filter(id=user_data['chat_id'])
        if chat.exists():
            chat = Chat.objects.get(id=user_data['chat_id'])
            # check if the user have privilige
            if chat.user_id_1.id == request.session['user']:
                if user_data['state'] == "confirmed":
                    if chat.state_1 == 'not_confirmed' and chat.state_2 == 'confirmed':
                        chat.state_1 = 'confirmed'
                        chat.save()
                        # both confirmed should do rating and delete from tradelist, wishlist and chat
                        # delete from tradelist and wishlist for user_id
                        if chat.suggestion_id == None:
                            user_id_giving_book = TradeList.objects.get(Q(givingBook_id=chat.match_id.giving_book) & Q(user_id=chat.match_id.user_id))
                            user_id_giving_book.delete()
                            user_id_wanted_book = WishList.objects.get(Q(book_id=chat.match_id.wanted_book) & Q(user_id=chat.match_id.user_id))
                            user_id_wanted_book.delete()
                            # delete from tradelist and wishlist for matched_user
                            matched_user_id_giving_book = WishList.objects.get(Q(book_id=chat.match_id.giving_book) & Q(user_id=chat.match_id.matched_user))
                            matched_user_id_giving_book.delete()
                            matched_user_id_wanted_book = TradeList.objects.get(Q(givingBook_id=chat.match_id.wanted_book) & Q(user_id=chat.match_id.matched_user))
                            matched_user_id_wanted_book.delete()

                            # delete the matches where wanted_book of the users and givingbooks exist
                            matches_1 = Match.objects.filter(Q(user_id=chat.match_id.user_id) & Q(giving_book=chat.match_id.giving_book))
                            if matches_1.exists():
                                for match_1 in matches_1:
                                    if match_1 == chat.match_id:
                                        continue
                                    else:
                                        match_1.delete()

                            matches_2 = Match.objects.filter(Q(user_id=chat.match_id.matched_user) & Q(giving_book=chat.match_id.wanted_book))
                            if matches_2.exists():
                                for match_2 in matches_2:
                                    if match_2 == chat.match_id:
                                        continue
                                    else:
                                        match_2.delete()
                        elif chat.match_id == None:
                            user_id_giving_book = TradeList.objects.get(Q(givingBook_id=chat.suggestion_id.giving_book) & Q(user_id=chat.suggestion_id.user_id))
                            user_id_giving_book.delete()
                            # delete from tradelist for suggested_user
                            suggested_user_id_giving_book = TradeList.objects.get(Q(givingBook_id=chat.suggestion_id.suggested_book_id) & Q(user_id=chat.suggestion_id.suggested_user))
                            suggested_user_id_giving_book.delete()

                            # delete the suggestions where wanted_book of the users and givingbooks exist
                            suggestions_1 = Suggestion.objects.filter(Q(user_id=chat.suggestion_id.user_id) & Q(giving_book=chat.suggestion_id.giving_book))
                            if suggestions_1.exists():
                                for suggestion_1 in suggestions_1:
                                    if suggestion_1 == chat.suggestion_id:
                                        continue
                                    else:
                                        suggestion_1.delete()
                            suggestions_2 = Suggestion.objects.filter(Q(user_id=chat.suggestion_id.suggested_user) & Q(giving_book=chat.suggestion_id.suggested_book_id))
                            if suggestions_2.exists():
                                for suggestion_2 in suggestions_2:
                                    if suggestion_2 == chat.suggestion_id:
                                        continue
                                    else:
                                        suggestion_2.delete()
                        status = 'success'
                        message = 'the trade was confirmed succesfully, please rate the user'
                    elif chat.state_1 == 'confirmed':
                        status = 'error'
                        message = 'the trade is already confirmed by you'
                    elif chat.state_1 == 'rejected':
                        status = 'error'
                        message = 'the trade is already rejected by you'
                    elif chat.state_1 == 'not_confirmed' and chat.state_2 == 'rejected':
                        chat.state_1 = 'rejected'
                        chat.save()
                        status = 'error'
                        message = 'the other user already rejected the trade, so the whole trade is rejected'
                    elif chat.state_1 == 'not_confirmed' and chat.state_2 == 'not_confirmed':
                        chat.state_1 = 'confirmed'
                        chat.save()
                        status = 'success'
                        message = 'the trade was confirmed succesfully, please wait the other user to confirm'
                elif user_data['state'] == "rejected":
                    if chat.state_1 == 'not_confirmed' and chat.state_2 == 'confirmed':
                        chat.state_1 = 'rejected'
                        chat.state_2 = 'rejected'
                        chat.save()
                        status = 'success'
                        message = 'the trade was rejected by you, which made the whole trade rejected'
                    elif chat.state_1 == 'rejected':
                        status = 'error'
                        message = 'the trade is already rejected by you'
                    elif chat.state_1 == 'confirmed':
                        status = 'error'
                        message = 'the trade is already confirmed by you'
                    elif chat.state_1 == 'not_confirmed' and chat.state_2 == 'not_confirmed':
                        chat.state_1 = 'rejected'
                        chat.state_2 = 'rejected'
                        chat.save()
                        status = 'success'
                        message = 'since you rejected the trade first, it was rejected for the other user too'
                    elif chat.state_1 == 'not_confirmed' and chat.state_2 == 'rejected':
                        chat.state_1 = 'rejected'
                        chat.save()
                        status = 'error'
                        message = 'the other user already rejected the trade, so the whole trade is rejected'
            elif chat.user_id_2.id == request.session['user']:
                if user_data['state'] == "confirmed":
                    if chat.state_2 == 'not_confirmed' and chat.state_1 == 'confirmed':
                        chat.state_2 = 'confirmed'
                        chat.save()
                        # both confirmed should do rating and delete from tradelist, wishlist and chat
                        # delete from tradelist and wishlist for user_id
                        if chat.suggestion_id == None:
                            user_id_giving_book = TradeList.objects.get(Q(givingBook_id=chat.match_id.giving_book) & Q(user_id=chat.match_id.user_id))
                            user_id_giving_book.delete()
                            user_id_wanted_book = WishList.objects.get(Q(book_id=chat.match_id.wanted_book) & Q(user_id=chat.match_id.user_id))
                            user_id_wanted_book.delete()
                            # delete from tradelist and wishlist for matched_user
                            matched_user_id_giving_book = WishList.objects.get(Q(book_id=chat.match_id.giving_book) & Q(user_id=chat.match_id.matched_user))
                            matched_user_id_giving_book.delete()
                            matched_user_id_wanted_book = TradeList.objects.get(Q(givingBook_id=chat.match_id.wanted_book) & Q(user_id=chat.match_id.matched_user))
                            matched_user_id_wanted_book.delete()

                            # delete the matches where wanted_book of the users and givingbooks exist
                            matches_1 = Match.objects.filter(Q(user_id=chat.match_id.user_id) & Q(giving_book=chat.match_id.giving_book))
                            if matches_1.exists():
                                for match_1 in matches_1:
                                    if match_1 == chat.match_id:
                                        continue
                                    else:
                                        match_2.delete()

                            matches_2 = Match.objects.filter(Q(user_id=chat.match_id.matched_user) & Q(giving_book=chat.match_id.wanted_book))
                            if matches_2.exists():
                                for match_2 in matches_2:
                                    if match_2 == chat.match_id:
                                        continue
                                    else:
                                        match_2.delete()
                        elif chat.match_id == None:
                            user_id_giving_book = TradeList.objects.get(Q(givingBook_id=chat.suggestion_id.giving_book) & Q(user_id=chat.suggestion_id.user_id))
                            user_id_giving_book.delete()
                            # delete from tradelist for suggested_user
                            suggested_user_id_giving_book = TradeList.objects.get(Q(givingBook_id=chat.suggestion_id.suggested_book_id) & Q(user_id=chat.suggestion_id.suggested_user))
                            suggested_user_id_giving_book.delete()

                            # delete the suggestions where wanted_book of the users and givingbooks exist
                            suggestions_1 = Suggestion.objects.filter(Q(user_id=chat.suggestion_id.user_id) & Q(giving_book=chat.suggestion_id.giving_book))
                            if suggestions_1.exists():
                                for suggestion_1 in suggestions_1:
                                    if suggestion_1 == chat.suggestion_id:
                                        continue
                                    else:
                                        suggestion_1.delete()

                            suggestions_2 = Suggestion.objects.filter(Q(user_id=chat.suggestion_id.suggested_user) & Q(giving_book=chat.suggestion_id.suggested_book_id))
                            if suggestions_2.exists():
                                for suggestion_2 in suggestions_2:
                                    if suggestion_2 == chat.suggestion_id:
                                        continue
                                    else:
                                        suggestion_2.delete()
                        status = 'success'
                        message = 'the trade was confirmed succesfully, please rate the user'
                    elif chat.state_2 == 'confirmed':
                        status = 'error'
                        message = 'the trade is already confirmed by you'
                    elif chat.state_2 == 'rejected':
                        status = 'error'
                        message = 'the trade is already rejected by you'
                    elif chat.state_2 == 'not_confirmed' and chat.state_1 == 'not_confirmed':
                        chat.state_2 = 'confirmed'
                        chat.save()
                        status = 'success'
                        message = 'the trade was confirmed succesfully, please wait the other user to confirm'
                    elif chat.state_2 == 'not_confirmed' and chat.state_1 == 'rejected':
                        chat.state_2 = 'rejected'
                        chat.save()
                        status = 'error'
                        message = 'the other user already rejected the trade, so the whole trade is rejected'
                elif user_data['state'] == "rejected":
                    if chat.state_2 == 'not_confirmed' and chat.state_1 == 'confirmed':
                        chat.state_2 = 'rejected'
                        chat.state_1 = 'rejected'
                        chat.save()
                        status = 'success'
                        message = 'the trade was rejected by you, which made the whole trade rejected'
                    elif chat.state_2 == 'rejected':
                        status = 'error'
                        message = 'the trade is already rejected by you'
                    elif chat.state_2 == 'confirmed':
                        status = 'error'
                        message = 'the trade is already confirmed by you'
                    elif chat.state_2 == 'not_confirmed' and chat.state_1 == 'not_confirmed':
                        chat.state_2 = 'rejected'
                        chat.state_1 = 'rejected'
                        chat.save()
                        status = 'success'
                        message = 'since you rejected the trade, it was automatically rejected for the other user too'
                    elif chat.state_2 == 'not_confirmed' and chat.state_1 == 'rejected':
                        chat.state_2 = 'rejected'
                        chat.save()
                        status = 'error'
                        message = 'the other user already rejected the trade, so the whole trade is rejected'
            else:
                status = 'error'
                message = 'you do not have a privilege to do this action'
        else:
            status = 'error'
            message = 'this chat does not exist'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


@api_view(['POST'])
def rate_user(request): # WORKS
    data = json.loads(request.body) # {"user_id":"1", "rating":"5"}
    if 'user' in request.session:
        if Chat.objects.filter((Q(user_id_1=request.session['user']) & Q(user_id_2=data['user_id'])) | (Q(user_id_2=request.session['user']) & Q(user_id_1=data['user_id']))).exists():
            chat = Chat.objects.get((Q(user_id_1=request.session['user']) & Q(user_id_2=data['user_id'])) | (Q(user_id_2=request.session['user']) & Q(user_id_1=data['user_id'])) & Q(match_id=data['match_id']) & Q(suggestion_id=data['suggestion_id']))
            if chat.state_1 == 'confirmed' and chat.state_2 == 'confirmed':
                if int(data['rating']) > 5 or int(data['rating']) < 1:
                    status = 'error'
                    message = 'the rating input is invalid'
                else:
                    status = 'success'
                    message = 'you succesfully rated the user'
                    rating = UserRating(rating_user=User.objects.get(id=request.session['user']), rated_user=User.objects.get(id=data['user_id']), rating=data['rating'])
                    rating.save()
            else:
                status = 'error'
                message = 'user cannot be rated without confirmation of trade'
        else:
            status = 'error'
            message = 'you cannot rate a user that you never had a trade with'
    else:
        status = 'error'
        message = 'you should login first'

    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


"""
------------------------------------------------------SEEDING AREA, DO NOT ENTER-----------------------------------------------
@api_view(['POST'])
def add_books(request):
    with open('C:\\Users\\Mehin\\Desktop\\book\\bookclub\\bookclub\\bookclub_server\\datasets\\BX-Books.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            p = Book(isbn=row['isbn'], title=row['title'], authorName=row['authorName'], publishDate=row['publishDate'], publisher=row['publisher'], bookPhoto=row['bookPhoto'])
            p.save()
    return JsonResponse({'success':'yes'})
@api_view(['POST'])
def seed_user(request):
    i = 0
    while i < 500:
        faker = Factory.create('tr_TR')
        name = faker.name()
        country = 'Turkey'
        mail = faker.email()
        phoneNumber = faker.phone_number()
        dateOfBirth = faker.date_of_birth(minimum_age=18, maximum_age=100)
        username = faker.user_name()
        password = faker.password(length=6, special_chars=False, digits=False, upper_case=False, lower_case=True)
        longitude = random.uniform(36, 42) 
        latitude = random.uniform(26,45)
        user = User(name=name, country=country, mail=mail, phoneNumber=phoneNumber, dateOfBirth=dateOfBirth, username=username, password=password,
                    long=longitude, lat=latitude, onlineState=1, profilePicture='noimage.jpg')
        user.save()
        user_settings = AccountSettings(user_id=user)
        user_settings.save()
        i += 1
    return JsonResponse({'success': 'yes'})
@api_view(['POST'])
def seed_wishlist(request):
    i = 1
    while i <= 489:
        wishlistSize = random.randint(0, 10)
        # print(tradelistSize)
        index = 0
        while index < wishlistSize:
            if i <= 50:
                book_id = random.randint(1, 30)
            else:
                book_id = random.randint(1, 25665)
            if WishList.objects.filter(book_id_id=book_id, user_id_id=i).count() == 1:
                continue
            else:
                wishlistRow = WishList(book_id_id=book_id, user_id_id=i, order=(index+1))
                wishlistRow.save()
            index = index + 1
        i = i + 1
    return JsonResponse({'success': 'yes'})
@api_view(['POST'])
def seed_tradelist(request):
    i = 1
    while i <= 489:
        tradelistSize = random.randint(0, 10)
       # print(tradelistSize)
        index = 0
        while index < tradelistSize:
            if i <= 50:
                add_book_id = random.randint(1, 30)
            else:
                add_book_id = random.randint(1, 25665)
            wishlistRow = WishList.objects.filter(Q(user_id=i) & Q(book_id=add_book_id))
            if (wishlistRow.exists()) or (TradeList.objects.filter(givingBook_id_id=add_book_id, user_id_id=i).count() == 1):
                continue
            else:
                tradelistRow = TradeList(givingBook_id_id=add_book_id, user_id_id=i)
                tradelistRow.save()
            index = index + 1
        i = i + 1
    return JsonResponse({'success': 'yes'})
"""