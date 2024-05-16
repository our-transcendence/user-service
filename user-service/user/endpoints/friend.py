import os

from django.db.models import Q
from django.http import response, HttpRequest, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from user.models import User, Friend

import json
import requests

import ourJWT.OUR_exception

from userService import settings
from user.utils import get_user_from_jwt

from django.db.models import Q
from django.db.models import F

NO_USER = 404, "No user found with given ID"
JSON_DECODE_ERROR = 400, "JSON Decode Error"
JSON_BAD_KEYS = 400, "JSON Bad Keys"
USER_EXISTS = 401, "User with this login already exists"
BAD_IDS = 400, "User id is not equal with connected user id"
CANT_CONNECT_AUTH = 408, "Cant connect to auth-service"
ONLY_PNG = 400, "Only png images are allowed"


@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def get_friends(request, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    # get all the friends and return them

    Friend.objects.filter(
        Q(user__friend__user=F('friend')) &
        Q(friend__user__friend=F('user')) &
        Q(user=user.id)
    )
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def get_friend_rec(request, user_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    # get all the friends requests you received
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def get_friend_send(request, user_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    # get all the friends requests you sent
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def add_friend(request, user_id, friend_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    # add the relation user_id to friend_id
    return response.HttpResponse()
