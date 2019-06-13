from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.utils import json

# in settings.py, find MIDDLEWARE_CLASSES and remove 'django.middleware.csrf.CsrfViewMiddleware'

def signup_email(request):
    user_data = json.loads(request.body)
    subject = 'Welcome to BookClub ' + user_data['username'] + '!'
    body = 'How are you? Thank you for joining the largest book club of our planet!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_data['mail']]
    if send_mail(subject, body, email_from, recipient_list, fail_silently=False) == 1:
        status = "success"
        message = "email sent successfully"
    else:
        status = "error"
        message = "email cannot be sent"
    json_data = {"status": status, "message": message}
    return JsonResponse(json_data)


def forgot_password_email(request):
    user_data = json.loads(request)
    subject = 'Forgot your password? Well, that happens sometimes.'
    body = 'Here is your new password: ' + user_data['new_password']
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_data['mail']]
    if send_mail(subject, body, email_from, recipient_list, fail_silently=False) == 1:
        status = "success"
        message = "email sent successfully"
    else:
        status = "error"
        message = "email cannot be sent"
    new_password = user_data['new_password']
    json_data = {"status": status, "message": message, "new_password": new_password}
    return JsonResponse(json_data)
