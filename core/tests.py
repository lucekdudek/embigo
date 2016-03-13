# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase

from core.helper import get_space_user, user_is_space_user
from core.models import Space, SpaceUser, Message
from core.rights import *


class HelperTests(TestCase):

    def test_get_space_user(self):
        space = Space()
        user = User()
        with self.assertRaises(SpaceUser.DoesNotExist): get_space_user(user, space)

    def test_user_is_space_user(self):
        space = Space()
        user = User()
        self.assertFalse(user_is_space_user(user, space))

class SpaceModelTests(TestCase):

    def test_Space_str(self):
        space = Space(name="")
        self.assertEqual(str(space), space.name)

    def test_user_can_SEE_UNDERSPACES(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(SEE_UNDERSPACES), False)

class SpaceUserTests(TestCase):

    def test_SpaceUser_str(self):
        space_user = SpaceUser(space=Space(name=""), user=User(username=""))
        self.assertEqual(str(space_user), "%s z %s"%(space_user.user.username, space_user.space.name))

    def test_user_can_CREATE_SPACE(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(CREATE_SPACE), False)

    def test_user_can_EDIT_SPACE(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(EDIT_SPACE), False)

    def test_user_can_ARCHIVE_SPACE(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(ARCHIVE_SPACE), False)

    def test_user_can_DELETE_SPACE(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(DELETE_SPACE), False)

    def test_user_can_ADD_USER(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(ADD_USER), False)

    def test_user_can_EDIT_RIGHTS(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(EDIT_RIGHTS), False)

    def test_user_can_SEE_USERS(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(SEE_USERS), False)

    def test_user_can_ADD_MESSAGE(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(ADD_MESSAGE), False)

    def test_user_can_SEE_MESSAGES(self):
        new_rights="000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(SEE_MESSAGES), False)

class MessageModelTests(TestCase):

    def test_Message_str(self):
        message = Message(content="")
        self.assertEqual(str(message), "%s"%(message.content))
