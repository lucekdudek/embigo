# -*- coding: utf-8 -*-
from uuid import uuid1
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import  render, get_object_or_404

from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user
from core.models import Space, SpaceUser
from django.contrib.auth import authenticate, login, logout

@login_required(login_url='/out/')
def index(request):
    space_users_list = SpaceUser.objects.filter(user=request.user)
    space_list = [su.space for su in space_users_list]
    context = {'space_list': space_list}
    return render(request, 'index.html', context)

def space(request, space_id):
    space = get_object_or_404(Space, pk=space_id)
    space_list = Space.objects.filter(parent=space_id)
    if user_is_space_user(request.user, space):
        context = {'space': space, 'space_list': space_list}
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
