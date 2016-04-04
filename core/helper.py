# -*- coding: utf-8 -*-
from core.models import Space, SpaceUser
from core.rights import SEE_UNDERSPACES


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

def user_default_rights():
    """
    :return: rights of normal user of space
    """
    return "111100011011"

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

def get_space_user_or_none(user, space):
    """
    :param user: user
    :param space: space
    :return: SpaceUser or None in the case of error SpaceUser.DoesNotExist
    """
    try:
        space_user = SpaceUser.objects.get(space=space, user=user)
    except SpaceUser.DoesNotExist:
        pass
    if 'space_user' in locals():
        return space_user
    else:
        return None

def user_see_child(user, parent_user, child):
    """
    :param user: user
    :param child: space wich can or cannot be seen
    :param parent_user: space_user of parent space to child
    :return: True/False
    """
    if parent_user:
        return child.is_public() or child.is_private() and (user_is_space_user(user, child) or parent_user.can(SEE_UNDERSPACES))
    else:
        return child.is_public() or child.is_private() and user_is_space_user(user, child)


