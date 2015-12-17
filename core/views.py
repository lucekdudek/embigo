# -*- coding: utf-8 -*-
import json
from uuid import uuid1

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import  render, get_object_or_404
from django.utils import timezone

from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user, space_is_channel, space_is_conversation, space_is_space, user_can, get_space_user
from core.models import Space, SpaceUser, Message
from core.rights import *


@login_required(login_url='/out/')
def index(request):
    return HttpResponseRedirect("/00000000-0000-0000-0000-000000000000")

@login_required(login_url='/out')
def space(request, space_id):
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    if user_is_space_user(user, space):
        try:
            space_user = get_space_user(user, space)
        except SpaceUser.DoesNotExist:
            return HttpResponseRedirect("/out")
        space_list = Space.objects.filter(parent=space_id).order_by('-status')
        channels = [s for s in space_list if space_is_channel(space=s)]
        conversations = [s for s in space_list if space_is_conversation(space=s) and user_is_space_user(user=user, space=s)]
        own_spaces = [s for s in space_list if space_is_space(space=s) and user_is_space_user(user=user, space=s)]
        other_spaces = [s for s in space_list if space_is_space(space=s) and user_can(SEE_UNDERSPACES, space_user)]
        other_spaces = [s for s in other_spaces if s not in own_spaces]
        collaborators = SpaceUser.objects.filter(space=space) if user_can(SEE_USERS, space_user) else []
        messages = Message.objects.filter(space=space).order_by('-data') if user_can(SEE_MESSAGES, space_user) else []
        can_add_message = user_can(ADD_MESSAGE, space_user)
        can_create_space = user_can(CREATE_SPACE, space_user)
        can_create_channel = user_can(CREATE_CHANNEL, space_user)
        can_create_conversation = user_can(CREATE_CONVERSATION, space_user)
        can_edit_space = user_can(EDIT_SPACE, space_user)
        can_archive_space = user_can(ARCHIVE_SPACE, space_user)
        can_delete_space = user_can(DELETE_SPACE, space_user)
        can_add_user = user_can(ADD_USER, space_user)
        can_edit_user_rights = user_can(EDIT_RIGHTS, space_user)
        context = {
            'space': space,
            'own_spaces': own_spaces,
            'other_spaces': other_spaces,
            'channels': channels,
            'conversations': conversations,
            'collaborators': collaborators,
            'messages': messages,
            'can_add_message': can_add_message,
            'can_create_space': can_create_space,
            'can_create_channel': can_create_channel,
            'can_create_conversation': can_create_conversation,
            'can_edit_space': can_edit_space,
            'can_archive_space': can_archive_space,
            'can_delete_space': can_delete_space,
            'can_add_user:': can_add_user,
            'can_edit_user_rights': can_edit_user_rights,
        }
        return render(request, 'space.html', context)
    else:
        return HttpResponseRedirect("/")

def signin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            errormessage = "Użytkownik jest nieaktywny."
            context = {'errormessage': errormessage}
            return render(request, 'signin.html', context)
    else:
        errormessage = "Wystąpił błąd autoryzacji."
        context = {'errormessage': errormessage}
        return render(request, 'signin.html', context)

def signout(request):
    logout(request)
    return render(request, 'signin.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_space_user = SpaceUser(uid=uuid1(), rights=embigo_default_rights(), space=embigo_main_space(), user=new_user)
            new_space_user.save()
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'register.html', context)

def new_message(request):
    if request.method == 'POST':
        context = {}

        space = Space.objects.get(uid=request.POST.get('space'))
        message = Message(uid=uuid1(), content=request.POST.get('content'), user=request.user, space=space, data=timezone.now())
        message.save()
        
        context['result'] = 'Create post successful!'
        context['content'] = message.content
        context['date'] = ""
        context['user'] = message.user.username
    else:
        context = {"nothing to see": "this isn't happening"}
    return HttpResponse(
            json.dumps(context),
            content_type="application/json"
        )

def edit_space(request):
    if request.method == 'POST':

        space = Space.objects.get(uid=request.POST.get('space'))
        space.name = request.POST.get('name')
        space.description = request.POST.get('description')
        space.save()
        
        context = 1
    else:
        context = 0
    return HttpResponse(
            json.dumps(context),
            content_type="application/json"
        )
