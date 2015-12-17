# -*- coding: utf-8 -*-
from core.models import Space, SpaceUser

def embigo_default_rights():
    """
    :return: rights of brand new user
    """
    return "010000000000"

def owner_default_rights():
    """
    :return: rights of creator of space
    """
    return "111111111111"

def embigo_main_space():
    """
    :return: star space
    """
    return Space.objects.get(uid="00000000-0000-0000-0000-000000000000")

def user_is_space_user(user, space):
    """
    :param user: get user
    :param space: get space
    :return: True if SpaceUser exist, else: False
    """
    try:
        su = SpaceUser.objects.get(space=space, user=user)
    except SpaceUser.DoesNotExist:
        pass
    except SpaceUser.MultipleObjectsReturned:
        pass
    return True if 'su' in locals() else False

def get_space_user(user, space):
    """
    note that this funcion can rasie error: paceUser.DoesNotExist
    :param user: user
    :param space: space
    :return: SpaceUser
    """
    return SpaceUser.objects.get(space=space, user=user)