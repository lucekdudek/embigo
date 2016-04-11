# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
from random import random
from uuid import uuid1

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Model
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.utils import timezone

from chat.chat import get_or_create_conversation
from core.crypto import encrypt, SECRET_KEY_WEBSOCKET
from core.forms import RegistrationForm, RecoveryForm
from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user, get_space_user, \
    owner_default_rights, user_default_rights, user_see_child, get_space_user_or_none, user_see_space
from core.models import Space, SpaceUser, Message, EmbigoUser, ChatMessage
from core.rights import *
from embigo.settings import WEBSOCKET_IP, WEBSOCKET_PORT


@login_required(login_url='/in/')
def index(request):
    """
    homepage
    redirect start space
    """
    try:
        emgibo_space = Space.objects.get(uid='00000000-0000-0000-0000-000000000000')
    except Space.DoesNotExist:
        emgibo_space = Space(
            uid='00000000-0000-0000-0000-000000000000',
            name='embigo',
            type=1,
            status=1,
        )
        emgibo_space.save()
    try:
        get_space_user(request.user, emgibo_space)
    except SpaceUser.DoesNotExist:
        space_user = SpaceUser(
            uid=uuid1(),
            rights=embigo_default_rights(),
            space=emgibo_space,
            user=request.user,
        )
        space_user.save()
    if request.get_full_path() == '/00000000-0000-0000-0000-000000000000/':
        return HttpResponseRedirect("/")
    else:
        return space(request)


@login_required(login_url='/in/')
def space(request, space_id='00000000-0000-0000-0000-000000000000'):
    """
    Display a space

    **Context**
        'space': this space
        'own_spaces': list of login user's spaces
        'other_spaces': list of login user's spaces witch user can see
        'collaborators': list of space's users
        'messages': list of space's messages
        'can_add_message': rights flag
        'can_create_space': rights flag
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
    if user_see_space(user, space):
        try:
            space_user = get_space_user(user, space)
        except SpaceUser.DoesNotExist:
            space_user = SpaceUser(uid=uuid1(), rights=embigo_default_rights(), space=space, user=user)
            space_user.save()

        children_list = [c for c in space.children.all() if c.is_active()]
        user_spaces = {}
        for c in children_list:
            if user_see_child(user, space_user, c):
                c_user = get_space_user_or_none(user, c)
                user_spaces[c] = [gc for gc in c.children.all() if gc.is_active() and user_see_child(user, c_user, gc)]

        parent_collaborators = []
        if space.parent:
            try:
                parent_user = SpaceUser.objects.get(space=space.parent, user=user)
            except SpaceUser.DoesNotExist:
                parent_user = None
            if parent_user and parent_user.can(SEE_USERS):
                parent_collaborators = SpaceUser.objects.filter(space=space.parent)
                parent_collaborators = [pc for pc in parent_collaborators if
                                        not user_is_space_user(pc.user, space) and space_user.can(SEE_USERS)]

        can_add_message = space_user.can(ADD_MESSAGE)
        can_create_space = space_user.can(CREATE_SPACE)
        can_edit_space = space_user.can(EDIT_SPACE)
        can_archive_space = space_user.can(ARCHIVE_SPACE)
        can_delete_space = space_user.can(DELETE_SPACE)
        can_add_user = space_user.can(ADD_USER)
        can_edit_user_rights = space_user.can(EDIT_RIGHTS)
        can_see_users = space_user.can(SEE_USERS)

        user_key = encrypt(SECRET_KEY_WEBSOCKET, request.session.session_key)

        websocket_server_address = 'ws://' + WEBSOCKET_IP + ':' + str(WEBSOCKET_PORT) + '/';

        context = {
            'space': space,

            'user_spaces': user_spaces,

            'parent_collaborators': parent_collaborators,

            'can_add_message': can_add_message,
            'can_create_space': can_create_space,
            'can_edit_space': can_edit_space,
            'can_archive_space': can_archive_space,
            'can_delete_space': can_delete_space,
            'can_add_user': can_add_user,
            'can_edit_user_rights': can_edit_user_rights,
            'can_see_users': can_see_users,

            'user_key': user_key,
            'websocket_server_address': websocket_server_address
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
            return HttpResponseRedirect(request.GET.get("next", "/"))
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'signin.html', context)


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
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.is_active = False
            new_user.save()
            new_space_user = SpaceUser(uid=uuid1(), rights=embigo_default_rights(), space=embigo_main_space(),
                                       user=new_user)
            new_space_user.save()
            salt = hashlib.sha1(str(random()).encode("utf-8")).hexdigest()[:5]
            activation_key = hashlib.sha1((salt + new_user.email).encode("utf-8")).hexdigest()
            key_expires = datetime.datetime.now() + datetime.timedelta(2)
            embigo_user = EmbigoUser(user=new_user, activation_key=activation_key, key_expires=key_expires,
                                     hash_type='ACTIVATE_HASH')
            embigo_user.save()
            email_subject = 'Embigo - Potwierdzenie Rejestracji '
            email_body = "Witaj %s, dziękujemy za rejestrację w Embigo. By zakończyć proces rejestracji musisz, w przeciągu" \
                         " 48 godzin kliknąć w poniższy link:\nhttp://87.206.25.188/confirm/%s" % (
                         new_user.username, activation_key)

            send_mail(email_subject, email_body, 'embigo@interia.pl', [new_user.email], fail_silently=False)
            return HttpResponseRedirect(request.GET.get("next", "/"), RequestContext(request))
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'register.html', context)


def edit_user(request):
    """
    Display forms for edit user

    **Context**
        user
        set password form
        notification

    **Template:**
    :template:`edit_user.html`
    """
    user = User.objects.get(id=request.user.id)
    form = SetPasswordForm(None)
    notification = None
    if request.method == 'POST':
        if request.POST.get('changePassword'):
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                notification = 'Hasło zostało zmienione! :)'
                update_session_auth_hash(request, form.user)
        elif request.POST.get('changeColor'):
            embigo_user = EmbigoUser.objects.get(user=user)
            embigo_user.color = request.POST.get('color')
            embigo_user.save()
            notification = 'Zmieniono kolor avatara! :)'
    context = {
        'user': request.user,
        'form': form,
        'notification': notification
    }
    return render(request, 'edit_user.html', context)


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
        message = Message(uid=uuid1(), content=request.POST.get('content'), user=request.user, space=space,
                          date=timezone.now())
        if request.FILES:
            message.file = request.FILES['file']
        message.save()
        context = {'result': 'Success', 'uid': str(message.uid), 'content': message.content,
                   'user': message.user.username, 'date': 'Dzisiaj'}
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
        space = Space(uid=uuid1(), name=request.POST.get('name'), description=request.POST.get('description'),
                      type=request.POST.get('type'), status=1, parent=spaceUid)
        space.save()
        spaceUser = SpaceUser(uid=uuid1(), rights=owner_default_rights(), space=space, user=request.user)
        spaceUser.save()
        for user_id in request.POST.getlist('new_space_users_id[]'):
            spaceUser = SpaceUser(uid=uuid1(), rights=user_default_rights(), space=space,
                                  user=User.objects.get(id=user_id))
            spaceUser.save()
        context = {'result': 'Success', 'space': str(space.uid)}
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
            spaceUser = SpaceUser(uid=uuid1(), rights=user_default_rights(), space=space,
                                  user=User.objects.get(id=user_id))
            spaceUser.save()
        context = {'result': 'Success'}
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required(login_url='/in/')
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
        space.status = (2 if space.status == 1 else 1)
        space.save()
        return HttpResponseRedirect("../")
    else:
        return HttpResponseRedirect("/")


@login_required(login_url='/in/')
def delete_space(request, space_id):
    """
    delete space

    **Context**
        delete button
    """
    user = request.user
    space = get_object_or_404(Space, pk=space_id)
    spaceUser = SpaceUser.objects.get(user=user, space=space)
    parent = space.parent
    if user_is_space_user(user, space) and spaceUser.can(DELETE_SPACE) and parent != None:
        space.delete()
        return HttpResponseRedirect("/%s" % (parent.uid))
    else:
        return HttpResponseRedirect("/")


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
        space.type = request.POST.get('type')
        space.save()
        context = True
    else:
        context = None
    return HttpResponse(json.dumps(context), content_type="application/json")


def activate(request, activation_key):
    try:
        embigo_user = EmbigoUser.objects.get(activation_key=activation_key)
        if embigo_user.key_expires > timezone.now() and embigo_user.hash_type == 'ACTIVATE_HASH':
            embigo_user.user.is_active = True
            embigo_user.user.save()
            embigo_user.activation_key = None
            embigo_user.hash_type = None
            embigo_user.save()
            context = {'message': "Twoje konto jest już aktywne"}
        else:
            context = {'message': "Błąd, podany link jest nieaktywny."}
    except ObjectDoesNotExist:
        context = {'message': "Błąd, podany link jest nieaktywny."}
    finally:
        return render(request, 'confirmation.html', context)


def recover_password(request):
    """
    Display form for recovering password

    **Context**
        recovery form

    **Template:**
    :template:`recovery.html`
    """
    if request.method == 'POST':
        form = RecoveryForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            salt = hashlib.sha1(str(random()).encode("utf-8")).hexdigest()[:5]
            activation_key = hashlib.sha1((salt + user.email).encode("utf-8")).hexdigest()
            key_expires = datetime.datetime.now() + datetime.timedelta(1)
            hash_type = "PASSWORD_HASH"
            embigo_user = EmbigoUser.objects.get(user=user)
            embigo_user.activation_key = activation_key
            embigo_user.key_expires = key_expires
            embigo_user.hash_type = hash_type
            embigo_user.save()
            email_subject = 'Embigo - odzyskiwanie hasła '
            email_body = "Witaj %s,\n aby zmienić swoje hasło w ciągu najbliższych 24 godzin kliknij w poniższy link:" \
                         "\nhttp://87.206.25.188/new_password/%s" % (user.username, activation_key)
            send_mail(email_subject, email_body, 'embigo@interia.pl', [user.email], fail_silently=False)
            return HttpResponseRedirect(request.GET.get("next", "/"), RequestContext(request))
    else:
        form = RecoveryForm()
    context = {'form': form}
    return render(request, 'recovery.html', context)


def new_password(request, activation_key):
    """
    Display form for recovering password

    **Context**
        set password Form

    **Template:**
    :template:`new_password.html`
    """
    try:
        embigo_user = EmbigoUser.objects.get(activation_key=activation_key)
        if embigo_user.key_expires > timezone.now() and embigo_user.hash_type == "PASSWORD_HASH":
            if request.method == 'POST':
                form = SetPasswordForm(embigo_user.user, request.POST)
                if form.is_valid():
                    embigo_user.activation_key = None
                    embigo_user.save()
                    form.save()
                    context = {'message': "Twoje hasło zostało zmienione"}
                    return render(request, 'confirmation.html', context)
            else:
                form = SetPasswordForm(embigo_user.user)
            context = {'form': form}
            return render(request, 'new_password.html', context)
        else:
            context = {'message': "Błąd, podany link jest nieaktywny."}
    except ObjectDoesNotExist:
        context = {'message': "Błąd, podany link jest nieaktywny."}
    return render(request, 'confirmation.html', context)
