from django.contrib import admin
from django.urls import path, include
from . import algorithm, chatservice, usercontroller, wishlistcontroller, accountsettingscontroller, tradelistcontroller, historycontroller, messagecontroller, chatcontroller
urlpatterns = [

    # usercontroller
    path('login/', usercontroller.login),
    path('signup/', usercontroller.signup),
    path('forgotPassword/', usercontroller.forgot_password),
    path('signout/', usercontroller.sign_out),
    path('getSession/', usercontroller.get_session),
    path('actionOnMatch/', usercontroller.action_on_match),
    path('actionOnSuggestion/', usercontroller.action_on_suggestion),
    path('seeOtherUserProfile/', usercontroller.see_other_user_profile),
    path('matchListIndex/', usercontroller.match_list_index),
    path('suggestionListIndex/', usercontroller.suggestion_list_index),
    path('mainMenuIndex/', usercontroller.main_menu_index),
    path('searchIndex/', usercontroller.search_index),
    path('getUserProfile/', usercontroller.get_user_profile),
    path('getUserProfileID/', usercontroller.get_user_profile_id),
    path('rate/', usercontroller.rate_user),
    path('getBook/', usercontroller.get_book),
    path('confirmTrade/', usercontroller.confirm_trade),
    path('searchBook/', usercontroller.search_book),
    path('userRating/', usercontroller.get_user_rating),

    # path('ekle/', usercontroller.add_books),
    # path('seed_user/', usercontroller.seed_user),
    # path('seed_wishlist/', usercontroller.seed_wishlist),
    # path('seed_tradelist/', usercontroller.seed_wishlist),

    # wishlistcontroller
    path('wishlist/index/', wishlistcontroller.index),
    path('wishlist/delete/', wishlistcontroller.delete),
    path('wishlist/add/', wishlistcontroller.add),
    path('wishlist/drag/', wishlistcontroller.drag),

    # accountsettingscontroller
    path('accountSettings/index/', accountsettingscontroller.index),
    path('accountSettings/reset/', accountsettingscontroller.reset),
    path('accountSettings/changeAvailability/', accountsettingscontroller.change_user_availability),
    path('accountSettings/changeMessagable/', accountsettingscontroller.change_user_messagable),
    path('accountSettings/lastSeen/', accountsettingscontroller.change_last_seen_state),
    path('accountSettings/changePicture/', accountsettingscontroller.change_profile_picture),
    path('accountSettings/changePhoneNumber/', accountsettingscontroller.change_phone_number),
    path('accountSettings/changeMail/', accountsettingscontroller.change_email),
    path('accountSettings/changeLocation/', accountsettingscontroller.change_location),
    path('accountSettings/onlineState/', accountsettingscontroller.change_online_state),
    path('accountSettings/changePassword/', accountsettingscontroller.change_password),

    # tradelistcontroller
    path('tradelist/index/', tradelistcontroller.index),
    path('tradelist/delete/', tradelistcontroller.delete),
    path('tradelist/add/', tradelistcontroller.add),
    # path('tradelist/update/', tradelistcontroller.update),

    # historycontroller
    path('history/index/match/', historycontroller.index_match),
    path('history/index/suggestion/', historycontroller.index_suggestion),
    path('history/clear/', historycontroller.clear),

    # chatcontroller
    path('chat/index/', chatcontroller.index),
    # chatservice methods
    path('chat/messageList/', chatservice.message_list),
    path('chat/send/', chatservice.send),
    path('chat/read/', chatservice.read),

    # messagecontroller
    path('message/index/', messagecontroller.index),

    # algorithm
    path('algo/match_algo/', algorithm.match_algorithm),
    path('algo/suggestion_algo/', algorithm.suggestion_algorithm)

]