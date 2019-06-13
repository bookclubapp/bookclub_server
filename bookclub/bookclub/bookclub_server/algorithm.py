import math
import re

import pandas as pd
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from django_pandas.io import read_frame
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import json
from .models import User, Match, TradeList, Suggestion, History, AccountSettings, UserRating, Chat, Book, WishList
from . import emailservice
from django.http import JsonResponse
from django.db.models import Q
import random
import datetime
import csv
from faker import Faker
from faker import Factory
import factory
import factory.django
import pandas as pd, numpy as np
from sklearn.cluster import DBSCAN


def locate_near_users(user):
    user_lat = user.lat
    user_long = user.long
    #    lat_difference = 0.318
    #    long_difference = 0.813
    # iki latitude arası distance 111 km, iki longitude arası mesafe (40 derece paralelinde) 86 km
    radius_lat_gt = user_lat + 0.318  # 0.81
    radius_long_gt = user_long + 0.416  # 2.1
    radius_lat_lt = user_lat - 0.318
    radius_long_lt = user_long - 0.416

    # get the users that are in the radius
    df = pd.DataFrame(list(User.objects.filter(
        (Q(lat__gte=user_lat) & Q(long__gte=user_long) & Q(lat__lte=radius_lat_gt) & Q(long__lte=radius_long_gt)) |
        (Q(lat__lte=user_lat) & Q(long__lte=user_long) & Q(lat__gte=radius_lat_lt) & Q(long__gte=radius_long_lt)) |
        (Q(lat__lte=user_lat) & Q(long__gte=user_long) & Q(lat__gte=radius_lat_lt) & Q(long__lte=radius_long_gt)) |
        (Q(lat__gte=user_lat) & Q(long__lte=user_long) & Q(lat__lte=radius_lat_gt) & Q(
            long__gte=radius_long_lt))).values()))
    # get their ids from the df

    ids = df.loc[:, 'id']
    return ids


def locate_near_5_users(user):
    near_user_ids = locate_near_users(user)
    if near_user_ids.shape[0] > 5:
        user_ratings = pd.DataFrame(columns=["near_id", "user_rating"])
        # user_ratings = []
        for near_id in near_user_ids:
            print("near_id", near_id)
            user_rating = calc_user_rating(near_id)
            user_ratings = user_ratings.append({"near_id": near_id, "user_rating": user_rating}, ignore_index=True)
            user_ratings = user_ratings.sort_values(by='user_rating', ascending=False)
        # user_ratings = sorted(user_ratings, key=lambda x: x[1], reverse=True)
        print("sorted user ratings: ", user_ratings)
        # users_to_return = [user_ratings[0][0], user_ratings[1][0], user_ratings[2][0]]

        dataframe = user_ratings["near_id"].iloc[:5]
        print("users_to_return: ", dataframe)
        return dataframe
    else:
        return near_user_ids


def calc_user_rating(matched_id):
    matched = UserRating.objects.filter(rated_user_id=matched_id)
    rate_sum = 0
    for rates in matched:
        rate_sum = rate_sum + rates.rating
    if len(matched) == 0:
        final_rate = 2.5
    else:
        final_rate = rate_sum / len(matched)
    return final_rate


def calc_user_distance_point(matched_id, user):
    long_distance = abs(User.objects.get(id=matched_id).long - user.long) / 0.012
    lat_distance = abs(User.objects.get(id=matched_id).lat - user.lat) / 0.009
    # print("long " + str(long_distance))
    # print("lat " + str(lat_distance))
    distance = math.sqrt((long_distance ** 2) + (lat_distance ** 2))
    print("distance: ", distance)
    distance_point = 50 - distance
    return distance_point


def calc_book_attribute_point(book_id_1, book_id_2):
    book_1 = Book.objects.get(id=book_id_1)
    book_2 = Book.objects.get(id=book_id_2)
    attr_point = 0
    if book_1.authorName.upper() == book_2.authorName.upper():
        attr_point = attr_point + 30
    if book_1.publisher.upper() == book_2.publisher.upper():
        attr_point = attr_point + 20
    return attr_point


def calc_wishlist_sim(book1_id, book2_id, user_id):
    df = pd.DataFrame(list(WishList.objects.filter(Q(book_id=book1_id) & ~Q(user_id=user_id)).values()))
    count = 0
    for item in df.iterrows():
        df2 = pd.DataFrame(list(WishList.objects.filter(user_id=item[1]["user_id_id"]).values()))
        for item2 in df2.iterrows():
            if item2[1]["book_id_id"] == book2_id:
                count = count + 1
    if count >= 4:
        wishlist_sim_point = 10
    elif count == 3:
        wishlist_sim_point = 7
    elif count == 2:
        wishlist_sim_point = 4
    elif count == 1:
        wishlist_sim_point = 1
    else:
        wishlist_sim_point = 0

    return wishlist_sim_point


@api_view(['GET'])
def match_algorithm(request):
    # latitude: 0.135 = 15 km, 0.009 = 1 km, 0.45 = 50 km
    # longitude: 0.35 = 15 km, 0.023 = 1 km, 1.15 = 50 km

    user = User.objects.get(id=request.session['user'])
    user_ids = locate_near_users(user)
    if not user_ids.empty:
        user_wishlist = pd.DataFrame(list(WishList.objects.filter(user_id=user.id).values()))
        if user_wishlist.empty:
            return JsonResponse({"status": 'error', "message": 'user does not have any books in wishlist'})
        user_tradelist = pd.DataFrame(list(TradeList.objects.filter(user_id=user.id).values()))
        if user_tradelist.empty:
            return JsonResponse({"status": 'error', "message": 'user does not have any books in tradelist'})
        user_desired_books = []
        user_giving_books = []
        books = user_wishlist.loc[:, 'book_id_id']
        for i in books:
            user_desired_books.append(i)
        first_matches = []
        for other_user_id in user_ids:
            if other_user_id != user.id:
                other_user_tradelist = pd.DataFrame(list(TradeList.objects.filter(user_id=other_user_id).values()))
                other_user_giving_books = []
                # print("other_user_tradelist", other_user_tradelist)
                if other_user_tradelist.empty:
                    continue
                books = other_user_tradelist.loc[:, 'givingBook_id_id']
                for i in books:
                    other_user_giving_books.append(i)
                common_books = []
                for giving_book in other_user_giving_books:
                    for wanted_book in user_desired_books:
                        if wanted_book == giving_book:
                            #  print("Match found " + str(wanted_book[0]) + " " + str(other_user_id))
                            common_books.append(wanted_book)
                if common_books:
                    first_matches.append([other_user_id, common_books])
        print("first_matches", first_matches, "size:", len(first_matches))  # ondan alacaklarim

        # if match is confirmed delete those books from tradelist and wishlist
        # if chat is confirmed delete the chat row

        books = user_tradelist.loc[:, 'givingBook_id_id']
        for i in books:
            user_giving_books.append(i)  # userin vermek istedigi kitaplarin idsi
        second_matches = []
        for i in range(len(first_matches)):
            other_user_id = (first_matches[i])[0]
            if other_user_id != user.id:
                other_user_wishlist = pd.DataFrame(list(WishList.objects.filter(user_id=other_user_id).values()))
                other_user_wanted_books = []
                if other_user_wishlist.empty:
                    continue
                books = other_user_wishlist.loc[:, 'book_id_id']
                for i in books:
                    other_user_wanted_books.append(i)
                common_books_2 = []
                for wanted_book in other_user_wanted_books:
                    for giving_book in user_giving_books:
                        if giving_book == wanted_book:
                            #  print("Match found " + str(wanted_book[0]) + " " + str(other_user_id))
                            common_books_2.append(giving_book)
                if common_books_2:
                    second_matches.append([other_user_id, common_books_2])
        print("second_matches", second_matches)  # ona vereceklerim
        final_matches = []
        for i in range(len(second_matches)):
            for j in range(len(first_matches)):
                if (second_matches[i])[0] == (first_matches[j])[0]:
                    final_matches.append([(second_matches[i])[0], (second_matches[i])[1],
                                          (first_matches[j])[1]])  # user_id, ona verceklerim, ondan alcaklarım

        print(final_matches)  # user_id, ona verceklerim, ondan alcaklarım
        if not len(final_matches) == 0:
            final_match_scores = []
            for i in range(len(final_matches)):
                matched_id = (final_matches[i])[0]
                final_rate = calc_user_rating(matched_id)
                final_rate = final_rate * 10
                print("user_rating point: " + str(final_rate))
                distance_point = calc_user_distance_point(matched_id, user)
                final_match_scores.append([matched_id, int(final_rate + distance_point)])
            print(final_match_scores)
            for j in range(len(final_matches)):
                matched_user_id = final_matches[j][0]
                for n in range(len(final_match_scores)):
                    if final_match_scores[n][0] == matched_user_id:
                        match_score = final_match_scores[n][1]
                        break
                for k in range(len(final_matches[j][1])):
                    giving_book_id = final_matches[j][1][k]
                    # print(giving_book_id)
                    for m in range(len(final_matches[j][2])):
                        wanted_book_id = final_matches[j][2][m]
                        match_table_row = Match.objects.filter(giving_book_id=giving_book_id, matched_user_id=matched_user_id,
                                                               user_id_id=user.id,
                                                               wanted_book_id=wanted_book_id)
                        if match_table_row.exists():
                            continue
                        else:
                            match_table_row = Match(match_score=match_score, state="pending",
                                                    match_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                                    giving_book_id=giving_book_id, matched_user_id=matched_user_id,
                                                    user_id_id=user.id,
                                                    wanted_book_id=wanted_book_id)
                            match_table_row.save()
        else:
            return JsonResponse({"status": 'error', "message": 'no matches found'})
    else:
        return JsonResponse({"status": 'error', "message": 'no near user found'})
    return JsonResponse({"status": 'success', "message": 'match algorithm generated the results'})


@api_view(['GET'])
def suggestion_algorithm(request):
    user = User.objects.get(id=request.session['user'])
    user_ids = locate_near_5_users(user)
    if not user_ids.empty:
        print(user_ids)
        user_wishlist = pd.DataFrame(list(WishList.objects.filter(user_id=user.id).values()))
        if user_wishlist.empty:
            return JsonResponse({"status": 'error', "message": 'user does not have any books in wishlist'})
        user_tradelist = pd.DataFrame(list(TradeList.objects.filter(user_id=user.id).values()))
        if user_tradelist.empty:
            return JsonResponse({"status": 'error', "message": 'user does not have any books in tradelist'})
        user_giving_books = []
        user_desired_books = []
        books = user_wishlist.loc[:, 'book_id_id']
        for i in books:
            user_desired_books.append(i)
        first_suggestion_scores = []
        #  user_ids_3 = [user_ids[0], user_ids[1], user_ids[2]]
        for other_user_id in user_ids:
            if other_user_id != user.id:
                other_user_tradelist = pd.DataFrame(list(TradeList.objects.filter(user_id=other_user_id).values()))
                other_user_giving_books = []
                # print("other_user_tradelist", other_user_tradelist)
                if other_user_tradelist.empty:
                    continue
                books = other_user_tradelist.loc[:, 'givingBook_id_id']
                for i in books:
                    other_user_giving_books.append(i)
                rating_point = calc_user_rating(other_user_id)
                distance_point = calc_user_distance_point(other_user_id, user)
                rating_point = 5 * rating_point
                print("user rating point" + str(rating_point))  # 25%
                distance_point = distance_point / 2  # 25%
                print("distance point" + str(distance_point))
                for giving_book in other_user_giving_books:
                    for wanted_book in user_desired_books:
                        if wanted_book != giving_book:
                            # first suggestion scorelar hesaplanacak
                            book_attr_point = calc_book_attribute_point(wanted_book, giving_book)
                            wishlist_sim_point = calc_wishlist_sim(wanted_book, giving_book, user.id)
                            book_attr_point = (3 * book_attr_point) / 5  # 30%
                            print("book_attr_point" + str(book_attr_point))
                            wishlist_sim_point = 2 * wishlist_sim_point  # 20%
                            print("wishlist_sim_point" + str(wishlist_sim_point))
                            suggestion_score = rating_point + distance_point + book_attr_point + wishlist_sim_point
                            if suggestion_score >= 30:
                                first_suggestion_scores.append(
                                    [other_user_id, giving_book, wanted_book, suggestion_score])
                            # appends other user's id, the book that is suggested, the book I wanted in my wishlist and score

        books = user_tradelist.loc[:, 'givingBook_id_id']
        for i in books:
            user_giving_books.append(i)  # userin vermek istedigi kitaplarin idsi
        second_suggestion_scores = []
        for other_user_id in user_ids:
            if other_user_id != user.id:
                other_user_wishlist = pd.DataFrame(list(WishList.objects.filter(user_id=other_user_id).values()))
                other_user_wanted_books = []
                if other_user_wishlist.empty:
                    continue
                books = other_user_wishlist.loc[:, 'book_id_id']
                for i in books:
                    other_user_wanted_books.append(i)
                rating_point = calc_user_rating(other_user_id)
                distance_point = calc_user_distance_point(other_user_id, user)
                rating_point = 5 * rating_point
                #  print("user rating point" + str(rating_point))
                distance_point = distance_point / 2
                # print("distance point" + str(distance_point))
                for wanted_book in other_user_wanted_books:
                    for giving_book in user_giving_books:
                        if wanted_book != giving_book:
                            # second suggestion scorelar hesaplanacak
                            book_attr_point = calc_book_attribute_point(wanted_book, giving_book)
                            wishlist_sim_point = calc_wishlist_sim(wanted_book, giving_book, user.id)
                            book_attr_point = 3 * book_attr_point / 5
                            # print("book_attr_point" + str(book_attr_point))
                            wishlist_sim_point = 2 * wishlist_sim_point
                            # print("wishlist_sim_point" + str(wishlist_sim_point))
                            suggestion_score = rating_point + distance_point + book_attr_point + wishlist_sim_point
                            if suggestion_score >= 30:
                                second_suggestion_scores.append([other_user_id, giving_book, suggestion_score])
                            # appends other user's id, the book I am giving and score
        final_suggestions = []
        suggestion_count = 0
        for i in range(len(first_suggestion_scores)):
            for j in range(len(second_suggestion_scores)):
                if (first_suggestion_scores[i])[0] == (second_suggestion_scores[j])[0]:
                  #  if suggestion_count < 50:
                    final_suggestion_row = [(first_suggestion_scores[i])[0], (first_suggestion_scores[i])[1],
                                                (second_suggestion_scores[j])[1], (first_suggestion_scores[i])[2],
                                                int(((first_suggestion_scores[i])[3] + (second_suggestion_scores[j])[
                                                    2]) / 2)]
                    if final_suggestion_row not in final_suggestions:
                        final_suggestions.append(final_suggestion_row)
                        suggestion_count = suggestion_count + 1
                  #  else:
                   #     break
            #if suggestion_count >= 50:
             #   break
                # appends other user's id, the book that is suggested, the book I am giving, the book I wanted in my wishlist,
                # the average of 2 suggestion scores
        if not len(final_suggestions) == 0:
            for j in range(len(final_suggestions)):
                other_user_id = final_suggestions[j][0]
                giving_book_id = final_suggestions[j][2]
                wanted_book_id = final_suggestions[j][3]
                suggested_book_id = final_suggestions[j][1]
                suggestion_score = int(final_suggestions[j][4])
                print("suggestion score: " + str(suggestion_score), "other_user_id: " + str(other_user_id),
                      "giving_book_id: " + str(giving_book_id), "suggested_book_id: " + str(suggested_book_id))
                suggestion_table_row = Suggestion.objects.filter(giving_book_id=giving_book_id,
                                                                 suggested_user_id=other_user_id,
                                                                 user_id_id=user.id,
                                                                 suggested_book_id_id=suggested_book_id)
                if suggestion_table_row.exists():
                    continue
                elif suggestion_score >= 30 and not WishList.objects.filter(Q(user_id_id=user.id) & Q(book_id_id=suggested_book_id)).exists():
                    suggestion_table_row = Suggestion(suggestion_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                                      recommendation_score=suggestion_score,
                                                      user_id_id=user.id, giving_book_id=giving_book_id,
                                                      state="pending",
                                                      suggested_user_id=other_user_id,
                                                      wanted_book_id=wanted_book_id,
                                                      suggested_book_id_id=suggested_book_id)
                    suggestion_table_row.save()
        else:
            return JsonResponse({"status": 'error', "message": 'no suggestions found'})
    else:
        return JsonResponse({"status": 'error', "message": 'no near user found'})
    return JsonResponse({"status": 'success', "message": 'suggestions created successfully'})