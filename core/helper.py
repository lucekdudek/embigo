# -*- coding: utf-8 -*-
from core.models import Space, SpaceUser

def embigo_default_rights():
    return "010000000000"

def embigo_main_space():
    return Space.objects.get(uid="00000000-0000-0000-0000-000000000000")

def user_is_space_user(user, space):
    try:
        su = SpaceUser.objects.get(space=space, user=user)
    except SpaceUser.DoesNotExist:
        pass
    except SpaceUser.MultipleObjectsReturned:
        pass
    return True if 'su' in locals() else False

def space_is_space(space):
    if space.type == 1: return True

def space_is_channel(space):
    if space.type == 2: return True

def space_is_conversation(space):
    if space.type == 3: return True

def user_can(right, space_user):
    if space_user != None:
        return int(space_user.rights[right])

def get_space_user(user, space):
    try:
        return SpaceUser.objects.get(space=space, user=user)
    except SpaceUser.DoesNotExist:
        pass
    except SpaceUser.MultipleObjectsReturned:
        pass