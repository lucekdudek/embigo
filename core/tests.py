# -*- coding: utf-8 -*-
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from chat.connected_users import ConnectedUsers
from core.helper import get_space_user, user_is_space_user, embigo_main_space, create_embigo_space, get_space_user_or_none, user_see_child, user_see_space
from core.models import Space, SpaceUser, Message
from core.rights import *
from core.views import signin, register


class ViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')

    def test_signin(self):
        request = self.factory.get('/in')
        request.user = self.user
        response = signin(request)
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        request = self.factory.get('/register')
        request.user = self.user
        response = register(request)
        self.assertEqual(response.status_code, 200)

    def test_edit_user(self):
        request = self.factory.get('/edit_user')
        request.user = self.user
        response = register(request)
        self.assertEqual(response.status_code, 200)


class HelperTests(TestCase):
    def test_get_space_user(self):
        space = Space()
        space.save()
        user = User()
        user.save()
        with self.assertRaises(SpaceUser.DoesNotExist): get_space_user(user, space)
        space_user = SpaceUser(user=user, space=space)
        space_user.save()
        self.assertEqual(get_space_user_or_none(user, space), space_user)
    
    def test_user_is_space_user(self):
        space = Space()
        user = User()
        self.assertFalse(user_is_space_user(user, space))
    
    def test_create_embigo_space(self):
        create_embigo_space()
        embigo = embigo_main_space()
        self.assertEqual(embigo.name, "embigo")
    
    def test_get_space_user_or_none(self):
        space = Space()
        space.save()
        user = User()
        user.save()
        self.assertEqual(get_space_user_or_none(user, space), None)
        space_user = SpaceUser(user=user, space=space)
        space_user.save()
        self.assertEqual(get_space_user_or_none(user, space), space_user)
    
    def test_user_see_child_01(self):
        user = User()
        user.save()
        child = Space()
        child.save()
        space_user = SpaceUser()
        self.assertFalse(user_see_child(user, space_user, child))

    def test_user_see_child_02(self):
        user = User()
        user.save()
        parent = Space()
        parent.save()
        child = Space(type=1)
        child.parent = parent
        child.save()
        space_user = SpaceUser()
        space_user.user = user
        space_user.space = parent
        space_user.save()
        self.assertTrue(user_see_child(user, space_user, child))

    def test_user_see_space(self):
        user = User()
        space = Space()
        self.assertFalse(user_see_space(user, space))

class SpaceModelTests(TestCase):
    def test_Space_str(self):
        space = Space(name="")
        self.assertEqual(str(space), space.name)

    def test_user_can_SEE_UNDERSPACES(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(SEE_UNDERSPACES), False)


class SpaceUserTests(TestCase):
    def test_SpaceUser_str(self):
        space_user = SpaceUser(space=Space(name=""), user=User(username=""))
        self.assertEqual(str(space_user), "%s z %s" % (space_user.user.username, space_user.space.name))

    def test_user_can_CREATE_SPACE(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(CREATE_SPACE), False)

    def test_user_can_EDIT_SPACE(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(EDIT_SPACE), False)

    def test_user_can_ARCHIVE_SPACE(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(ARCHIVE_SPACE), False)

    def test_user_can_DELETE_SPACE(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(DELETE_SPACE), False)

    def test_user_can_ADD_USER(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(ADD_USER), False)

    def test_user_can_EDIT_RIGHTS(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(EDIT_RIGHTS), False)

    def test_user_can_SEE_USERS(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(SEE_USERS), False)

    def test_user_can_ADD_MESSAGE(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(ADD_MESSAGE), False)

    def test_user_can_SEE_MESSAGES(self):
        new_rights = "000000000000"
        space_user = SpaceUser(rights=new_rights)
        self.assertEqual(space_user.can(SEE_MESSAGES), False)


class MessageModelTests(TestCase):
    def test_Message_str(self):
        message = Message(content="")
        self.assertEqual(str(message), "%s" % (message.content))

class ChatTest(TestCase):
    def test_add_and_get_Connected_User(self):
        user = User(is_superuser=1, username="admin")
        user.save()

        user = User.objects.get(username="admin")
        connected = ConnectedUsers()
        connected.add(1, user)
        self.assertEqual(str(connected.get(1)), "%s" % "admin")
        connected.remove(1)

    def test_is_online(self):
        user = User(is_superuser=1, username="admin")
        user.save()

        user = User.objects.get(username="admin")
        connected = ConnectedUsers()
        connected.add(1, user)
        print(connected.is_online("admin"))
        self.assertEqual(connected.is_online("admin"), True)
        self.assertEqual(connected.is_online("admin1"), False)
