# -*- coding: utf-8 -*-
import json
from uuid import uuid1

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import  render, get_object_or_404
from django.utils import timezone, formats

from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user, get_space_user, \
    owner_default_rights, user_default_rights
from core.models import Space, SpaceUser, Message
from core.rights import *


@login_required(login_url='/in/')
def index(request):
    """
    homepage
    redirect start space
    """
    return HttpResponseRedirect("/00000000-0000-0000-0000-000000000000")

@login_required(login_url='/in')
def space(request, space_id):
    """
    Display a space

    **Context**
        'space': this space
        'own_spaces': list of login user's spaces
        'other_spaces': list of login user's spaces witch user can see
        'own_channels': list of login user's channels
        'other_channels': list of login user's channels witch user can see
        'conversations': list of login user's conversations
        'collaborators': list of space's users
        'messages': list of space's messages
        'can_add_message': rights flag
        'can_create_space': rights flag
        'can_create_channel': rights flag
        'can_create_conversation': rights flag
        'can_edit_space': rights flag
        'can_archive_space': rights flag
        'can_delete_space': rights flag
        'can_add_user:': rights flag
        'can_edit_user_rights': rights flag

    **Template:**
    :template:`space.html`
    """
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    if user_is_space_user(user, space):
        try:
            space_user = get_space_user(user, space)
        except SpaceUser.DoesNotExist:
            return HttpResponseRedirect("/out")
        space_users = SpaceUser.objects.filter(space=space)
        space_list = Space.objects.filter(parent=space_id).order_by('-status')
        own_channels = [s for s in space_list if s.is_channel() and user_is_space_user(user=user, space=s)]
        other_channels = [s for s in space_list if s.is_channel()]
        other_channels = [s for s in other_channels if s not in own_channels]
        conversations = [s for s in space_list if s.is_conversation() and user_is_space_user(user=user, space=s)]
        own_spaces = [s for s in space_list if s.is_space() and user_is_space_user(user=user, space=s)]
        other_spaces = [s for s in space_list if s.is_space() and space_user.can(SEE_UNDERSPACES)]
        other_spaces = [s for s in other_spaces if s not in own_spaces]
        collaborators = SpaceUser.objects.filter(space=space) if space_user.can(SEE_USERS) else []
        messages = Message.objects.filter(space=space).order_by('-date') if space_user.can(SEE_MESSAGES) else []
        parent_collaborators = []
        if space.parent:
            try:
                parent_user = SpaceUser.objects.get(space=space.parent, user=user)
            except SpaceUser.DoesNotExist:
                parent_user = None
            if parent_user and parent_user.can(SEE_USERS):
                parent_collaborators = SpaceUser.objects.filter(space=space.parent)
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
            'space_users': space_users,
            'own_spaces': own_spaces,
            'other_spaces': other_spaces,
            'own_channels': own_channels,
            'other_channels': other_channels,
            'conversations': conversations,
            'collaborators': collaborators,
            'parent_collaborators': parent_collaborators,
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
    """
    Display form for login

    **Context**
        login form

    **Template:**
    :template:`signin.html`
    """
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
    """
    Log out and redirect to homepage
    """
    logout(request)
    return HttpResponseRedirect("/")

def register(request):
    """
    Display form for registration

    **Context**
        registration form

    **Template:**
    :template:`register.html`
    """
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
    """
    Display form for message

    **Context**
        message form

    **Template:**
    :template:`form_new_message.html`
    """
    if request.method == 'POST':
        space = Space.objects.get(uid=request.POST.get('space'))
        message = Message(uid=uuid1(), content=request.POST.get('content'), user=request.user, space=space, date=timezone.now())
        if request.FILES:
            message.file = request.FILES['file']
        message.save()
        context = {'result':'Success', 'uid': str(message.uid), 'content':message.content,'user': message.user.username, 'date': 'Dzisiaj'}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def delete_message(request):
    """
    delete message

    **Context**
        delete button
    """
    if request.method == 'POST':
        message = Message.objects.get(uid=request.POST.get('message'))
        message.delete()
        context = True
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def new_space(request):
    """
    Display form for space

    **Context**
        space form

    **Template:**
    :template:`form_new_space.html`
    """
    if request.method == 'POST':
        spaceUid = Space.objects.get(uid=request.POST.get('space'))
        space = Space(uid=uuid1(), name=request.POST.get('name'), description=request.POST.get('description'), type=1, status=1, parent=spaceUid)
        space.save()
        spaceUser = SpaceUser(uid=uuid1(), rights=owner_default_rights(), space=space, user=request.user)
        spaceUser.save()
        for user_id in request.POST.getlist('new_space_users_id[]'):
            spaceUser = SpaceUser(uid=uuid1(), rights=user_default_rights(), space=space, user=User.objects.get(id=user_id))
            spaceUser.save()
        context = {'result':'Success', 'space': str(space.uid)}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def add_collaborators(request):
    """
    Display form for adding collaborators

    **Context**
        add collaborators form

    **Template:**
    :template:`form_collaborators.html`
    """
    if request.method == 'POST':
        space = Space.objects.get(uid=request.POST.get('space'))
        for user_id in request.POST.getlist('new_collaborators_id[]'):
            spaceUser = SpaceUser(uid=uuid1(), rights=user_default_rights(), space=space, user=User.objects.get(id=user_id))
            spaceUser.save()
        context = {'result':'Success'}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

@login_required(login_url='/in')
def archive_space(request, space_id):
    """
    change status to archive

    **Context**
        achive button
    """
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    spaceUser = SpaceUser.objects.get(user=user, space=space)
    if user_is_space_user(user, space) and spaceUser.can(ARCHIVE_SPACE):
        space.status=(2 if space.status==1 else 1)
        space.save()
        return HttpResponseRedirect("../")
    else:
        return HttpResponseRedirect("/")

@login_required(login_url='/in')
def delete_space(request, space_id):
    """
    delete space

    **Context**
        delete button
    """
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    spaceUser = SpaceUser.objects.get(user=user, space=space)
    if user_is_space_user(user, space) and spaceUser.can(DELETE_SPACE):
        parent=space.parent
        space.delete()
        return HttpResponseRedirect("/%s"%(parent.uid))
    else:
        return HttpResponseRedirect("/")

def new_channel(request):
    """
    Display form for channel

    **Context**
        channel form

    **Template:**
    :template:`form_new_channel.html`
    """
    if request.method == 'POST':
        spaceUid = Space.objects.get(uid=request.POST.get('space'))
        channel = Space(uid=uuid1(), name=request.POST.get('name'), description=request.POST.get('description'), type=2, status=1, parent=spaceUid)
        channel.save()
        spaceUser = SpaceUser(uid=uuid1(), rights=owner_default_rights(), space=channel, user=request.user)
        spaceUser.save()
        context = {'result':'Success', 'space': str(channel.uid)}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

@login_required(login_url='/in')
def enter_channel(request, space_id, channel_id):
    """
    Add login user to chanel as SpaceUser

    **Context**
        endter chanel button
    """
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    if user_is_space_user(user, space):
        channel = Space.objects.get(uid=channel_id)
        new_spaceUser = SpaceUser(uid=uuid1(), rights=user_default_rights(), space=channel, user=request.user)
        new_spaceUser.save()
        return HttpResponseRedirect("/%s"%(channel_id))
    else:
        return HttpResponseRedirect("/")


def new_conversation(request):
    """
    Display form for conversation

    **Context**
        conversation form

    **Template:**
    :template:`form_new_conversation.html`
    """
    if request.method == 'POST':
        print(request.POST.get('space'))
        # spaceUid = Space.objects.get(uid=request.POST.get('space'))
        # conversation = Space(uid=uuid1(), name=request.POST.get('name'), description=request.POST.get('description'), type=2, status=1, parent=spaceUid)
        # conversation.save()
        # spaceUser = SpaceUser(uid=uuid1(), rights=owner_default_rights(), space=conversation, user=request.user)
        # spaceUser.save()
        # context = {'result':'Success', 'space': str(conversation.uid)}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")

def edit_space(request):
    """
    Display form for edit space

    **Context**
        edit space form

    **Template:**
    :template:`form_edit_space.html`
    """
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

def signin(request):
    """
    Display form for login

    **Context**
        login form

    **Template:**
    :template:`signin.html`
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect("/")
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'signin.html', context)
