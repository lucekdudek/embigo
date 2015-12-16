# -*- coding: utf-8 -*-
from uuid import uuid1
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import  render, get_object_or_404

from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user
from core.models import Space, SpaceUser, Message
from django.contrib.auth import authenticate, login, logout

import json

@login_required(login_url='/out/')
def index(request):
    space_users_list = SpaceUser.objects.filter(user=request.user)
    space_list = [su.space for su in space_users_list]
    context = {'space_list': space_list}
    return render(request, 'index.html', context)

def space(request, space_id):
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    if user_is_space_user(user, space):
        space_list = Space.objects.filter(parent=space_id)
        space_list = [s for s in space_list if user_is_space_user(user=user, space=s)]
        message_list = Message.objects.filter(space=space_id, user=user).order_by('-data')
        context = {'space': space, 'space_list': space_list, 'message_list': message_list}
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
        message = Message(uid=uuid1(), content=request.POST.get('content'), user=request.user, space=space, data=datetime.now())
        message.save()
        
        context['result'] = 'Create post successful!'
        context['content'] = message.content
        context['date'] = message.data.strftime('%B %d, %Y %I:%M %p')
        context['user'] = message.user.username
    else:
        context = {"nothing to see": "this isn't happening"}
    return HttpResponse(
            json.dumps(context),
            content_type="application/json"
        )
