# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
from random import random
from uuid import uuid1

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import  render, get_object_or_404
from django.template import RequestContext
from django.utils import timezone, formats

from core.forms import RegistrationForm, RecoveryForm
from core.helper import embigo_default_rights, embigo_main_space, user_is_space_user, get_space_user, \
    owner_default_rights, user_default_rights
from core.models import Space, SpaceUser, Message, EmbigoUser
from core.rights import *
from core.crypto import *


@login_required(login_url='/in/')
def index(request):
    """
    homepage
    redirect start space
    """
    try:
        emgibo_space=Space.objects.get(uid='00000000-0000-0000-0000-000000000000')
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
    if user_is_space_user(user, space):
        try:
            space_user = get_space_user(user, space)
        except SpaceUser.DoesNotExist:
            return HttpResponseRedirect("/out")
        space_users = SpaceUser.objects.filter(space=space)
        space_list = Space.objects.filter(parent=space_id).order_by('-status')
        own_spaces = [s for s in space_list if user_is_space_user(user=user, space=s)]
        other_spaces = [s for s in space_list if space_user.can(SEE_UNDERSPACES)]
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
                space_user_users = [s.user for s in collaborators]
                parent_collaborators = SpaceUser.objects.filter(space=space.parent)
                parent_collaborators = [pc for pc in parent_collaborators if pc.user not in space_user_users]
        can_add_message = space_user.can(ADD_MESSAGE)
        can_create_space = space_user.can(CREATE_SPACE)
        can_edit_space = space_user.can(EDIT_SPACE)
        can_archive_space = space_user.can(ARCHIVE_SPACE)
        can_delete_space = space_user.can(DELETE_SPACE)
        can_add_user = space_user.can(ADD_USER)
        can_edit_user_rights = space_user.can(EDIT_RIGHTS)

        user_key = encrypt(SECRET_KEY_WEBSOCKET,request.session.session_key)
        context = {
            'space': space,
            'space_users': space_users,
            'own_spaces': own_spaces,
            'other_spaces': other_spaces,
            'collaborators': collaborators,
            'parent_collaborators': parent_collaborators,
            'messages': messages,
            'can_add_message': can_add_message,
            'can_create_space': can_create_space,
            'can_edit_space': can_edit_space,
            'can_archive_space': can_archive_space,
            'can_delete_space': can_delete_space,
            'can_add_user': can_add_user,
            'can_edit_user_rights': can_edit_user_rights,
            'user_key': user_key
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
            return HttpResponseRedirect(request.GET.get("next","/"))
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
            new_space_user = SpaceUser(uid=uuid1(), rights=embigo_default_rights(), space=embigo_main_space(), user=new_user)
            new_space_user.save()
            salt = hashlib.sha1(str(random()).encode("utf-8")).hexdigest()[:5]
            activation_key = hashlib.sha1((salt+new_user.email).encode("utf-8")).hexdigest()
            key_expires = datetime.datetime.now() + datetime.timedelta(2)
            embigo_user = EmbigoUser(user=new_user, activation_key=activation_key, key_expires=key_expires, hash_type='ACTIVATE_HASH')
            embigo_user.save()
            email_subject = 'Embigo - Potwierdzenie Rejestracji '
            email_body = "Witaj %s, dziękujemy za rejestrację w Embigo. By zakończyć proces rejestracji musisz, w przeciągu" \
                         " 48 godzin kliknąć w poniższy link:\nhttp://87.206.25.188/confirm/%s" % (new_user.username, activation_key)
            send_mail(email_subject, email_body, 'embigo@interia.pl', [new_user.email], fail_silently=False)
            return HttpResponseRedirect(request.GET.get("next","/"), RequestContext(request))
    else:
        form = RegistrationForm()
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
        space.status=(2 if space.status==1 else 1)
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
    parent=space.parent
    if user_is_space_user(user, space) and spaceUser.can(DELETE_SPACE) and parent!=None:
        space.delete()
        return HttpResponseRedirect("/%s"%(parent.uid))
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
            activation_key = hashlib.sha1((salt+user.email).encode("utf-8")).hexdigest()
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
            return HttpResponseRedirect(request.GET.get("next","/"), RequestContext(request))
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

