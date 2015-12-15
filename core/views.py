# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import  render, get_object_or_404
from core.models import Space, SpaceUser
from django.contrib.auth import authenticate, login, logout

def user_is_space_user(user, space):
    return SpaceUser.objects.get(space=space) in SpaceUser.objects.filter(user=user)

@login_required(login_url='/out/')
def index(request):
    space_users_list = SpaceUser.objects.filter(user=request.user)
    space_list = [su.space for su in space_users_list]
    context = {'space_list': space_list}
    return render(request, 'index.html', context)

def space(request, space_id):
    space = get_object_or_404(Space, pk=space_id)
    if user_is_space_user(request.user, space):
        context = {'space': space}
        return render(request, 'space.html', context)
    else:
        return index(request)

def signin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return index(request)
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
