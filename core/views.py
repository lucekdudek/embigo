# -*- coding: utf-8 -*-
import json
from uuid import uuid1

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import  render, get_object_or_404
from django.utils import timezone

from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user, get_space_user, \
    owner_default_rights
from core.models import Space, SpaceUser, Message
from core.rights import *


@login_required(login_url='/in/')
def index(request):
    return HttpResponseRedirect("/00000000-0000-0000-0000-000000000000")

@login_required(login_url='/in')
def space(request, space_id):
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    if user_is_space_user(user, space):
        try:
            space_user = get_space_user(user, space)
        except SpaceUser.DoesNotExist:
            return HttpResponseRedirect("/out")
        space_list = Space.objects.filter(parent=space_id).order_by('-status')
        own_channels = [s for s in space_list if s.is_channel() and user_is_space_user(user=user, space=s)]
        other_channels = [s for s in space_list if s.is_channel()]
        other_channels = [s for s in other_channels if s not in own_channels]
        conversations = [s for s in space_list if s.is_conversation() and user_is_space_user(user=user, space=s)]
        own_spaces = [s for s in space_list if s.is_space() and user_is_space_user(user=user, space=s)]
        other_spaces = [s for s in space_list if s.is_space() and space_user.can(SEE_UNDERSPACES)]
        other_spaces = [s for s in other_spaces if s not in own_spaces]
        collaborators = SpaceUser.objects.filter(space=space) if space_user.can(SEE_USERS) else []
        messages = Message.objects.filter(space=space).order_by('-data') if space_user.can(SEE_MESSAGES) else []
        can_add_message = space_user.can(ADD_MESSAGE)
        can_create_space = space_user.can(CREATE_SPACE)
        can_create_channel = space_user.can(CREATE_CHANNEL)
        can_create_conversation = space_user.can(CREATE_CONVERSATION)
        can_edit_space = space_user.can(EDIT_SPACE)
        can_archive_space = space_user.can(ARCHIVE_SPACE)
        can_delete_space = space_user.can(DELETE_SPACE)
        can_add_user = space_user.can(ADD_USER)
        can_edit_user_rights = space_user.can(EDIT_RIGHTS)
        context = {
            'space': space,
            'own_spaces': own_spaces,
            'other_spaces': other_spaces,
            'own_channels': own_channels,
            'other_channels': other_channels,
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
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect("/")
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'signin.html', context)
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     user = authenticate(username=username, password=password)
    #     if user is not None:
    #         if user.is_active:
    #             login(request, user)
    #             return HttpResponseRedirect("/")
    #         else:
    #             errormessage = "Użytkownik jest nieaktywny."
    #             context = {'errormessage': errormessage}
    #             return render(request, 'signin.html', context)
    #     else:
    #         errormessage = "Wystąpił błąd autoryzacji."
    #         context = {'errormessage': errormessage}
    #         return render(request, 'signin.html', context)
    # else:
    #     return render(request, 'signin.html')


def signout(request):
    logout(request)
    return HttpResponseRedirect("/")

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
        space = Space.objects.get(uid=request.POST.get('space'))
        message = Message(uid=uuid1(), content=request.POST.get('content'), user=request.user, space=space, data=timezone.now())
        message.save()
        context = {'result':'Success', 'content':message.content,'user': message.user.username}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def new_space(request):
    if request.method == 'POST':
        spaceUid = Space.objects.get(uid=request.POST.get('space'))
        space = Space(uid=uuid1(), name=request.POST.get('name'), description=request.POST.get('description'), type=1, status=1, parent=spaceUid)
        space.save()
        spaceUser = SpaceUser(uid=uuid1(), rights=owner_default_rights(), space=space, user=request.user)
        spaceUser.save()
        context = {'result':'Success', 'space': str(space.uid)}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def new_channel(request):
    if request.method == 'POST':
        spaceUid = Space.objects.get(uid=request.POST.get('space'))
        space = Space(uid=uuid1(), name=request.POST.get('name'), description=request.POST.get('description'), type=2, status=1, parent=spaceUid)
        space.save()
        spaceUser = SpaceUser(uid=uuid1(), rights=owner_default_rights(), space=space, user=request.user)
        spaceUser.save()
        context = {'result':'Success', 'space': str(space.uid)}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def edit_space(request):
    if request.method == 'POST':
        space = Space.objects.get(uid=request.POST.get('space'))
        space.name = request.POST.get('name')
        space.description = request.POST.get('description')
        space.status = request.POST.get('status')
        space.save()
        context = True
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")
