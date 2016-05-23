# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase

from chat.connected_users import ConnectedUsers
from core.helper import get_space_user, user_is_space_user, embigo_main_space, create_embigo_space, get_space_user_or_none, user_see_child, user_see_space
from core.models import Space, SpaceUser, Message
from core.rights import *


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
    
    def test_user_see_child(self):
        user = User()
        child = Space()
        space_user = SpaceUser()
        self.assertFalse(user_see_child(user, space_user, child))
        #TODO more asserts
    
    def test_user_see_space(self):
        user = User()
        space = Space()
        self.assertFalse(user_see_space(user, space))
        #TODO more asserts

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

class RegistrationTest(TestCase):
    def test_call_view_empty_form(self):
        response = self.client.post('/register/', {}) # blank data dictionary
        self.assertFormError(response, 'form', 'username', 'To pole jest wymagane.')
        self.assertFormError(response, 'form', 'email', 'To pole jest wymagane.')
        self.assertFormError(response, 'form', 'password1', 'To pole jest wymagane.')
        self.assertFormError(response, 'form', 'password2', 'To pole jest wymagane.')

    def test_call_view_invalid_email(self):
        response = self.client.post('/register/', {'email': "abcd"})
        self.assertFormError(response, 'form', 'email', 'Wprowadź poprawny adres email.')

    def test_call_view_existing_email(self):
        user = User()
        user.email = 'aaaa@gmail.com'
        user.save()
        response = self.client.post('/register/', {'email': "aaaa@gmail.com"})
        self.assertFormError(response, 'form', 'email', 'Ten adres email jest już zarejestrowany.Proszę wprowadź inny adres email.')

    def test_call_view_different_password(self):
        response = self.client.post('/register/', {'password1': "abcd", 'password2': "abcde"})
        self.assertFormError(response, 'form', 'password2', 'Hasła się nie zgadzają.')

    def test_call_view_short_common_password(self):
        response = self.client.post('/register/', {'password1': "abcd", 'password2': "abcd"})
        self.assertFormError(response, 'form', 'password2', ['To hasło jest za krótkie. Musi zawierać co najmniej 8 znaków.', 'To hasło jest zbyt powszechne.'])

    def test_call_view_short_password(self):
        response = self.client.post('/register/', {'password1': "a2cd", 'password2': "a2cd"})
        self.assertFormError(response, 'form', 'password2', 'To hasło jest za krótkie. Musi zawierać co najmniej 8 znaków.')

    def test_call_view_common_password(self):
        response = self.client.post('/register/', {'password1': "aaaaaaaa", 'password2': "aaaaaaaa"})
        self.assertFormError(response, 'form', 'password2', 'To hasło jest zbyt powszechne.')

    def test_call_view_existing_user(self):
        user = User()
        user.username = 'aaaa'
        user.save()
        response = self.client.post('/register/', {'username': "aaaa"})
        self.assertFormError(response, 'form', 'username', 'Użytkownik o tej nazwie już istnieje.')
