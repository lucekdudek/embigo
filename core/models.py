# -*- coding: utf-8 -*-

import os.path
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone


class EmbigoUser(models.Model):
    class Meta:
        verbose_name = "użytkownik embigo"
        verbose_name_plural = "użytkownicy embigo"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, null=True, blank=True)
    activation_key = models.CharField(max_length=40, null=True, blank=True)
    key_expires = models.DateTimeField(default=timezone.now)
    hash_type = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.user.username)


def get_color(self):
    try:
        color = self.embigouser.color
    except ObjectDoesNotExist:
        colors = ["#FEE6AA","#FDD777","#FCC845","#FBBA13","#FEAAAA","#FD7777","#FC4545","#FB1313","#EBAAFE","#E077FD","#D545FC","#C913FB","#B9AAFE","#9077FD","#6745FC","#3E13FB","#AAE0FE","#77CEFD","#45BCFC","#13AAFB","#AAFECA","#77FDAB","#45FC8B","#13FB6C"]
        color = random.sample(colors,  1)[0];
        embigo_user = EmbigoUser(user=self, color=color)
        embigo_user.save()
        color = self.embigouser.color
    return color


User.add_to_class('get_color', get_color)


class Space(models.Model):
    class Meta:
        verbose_name = "przestrzeń"
        verbose_name_plural = "przestrzenie"

    uid = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return "%s" % (self.name)

    def get_path(self):
        paths = []
        parent = self.parent
        while parent != None:
            paths.append(parent)
            parent = parent.parent
        return paths[::-1]

    def space_users(self):
        return SpaceUser.objects.filter(space=self)

    def messages(self):
        return Message.objects.filter(space=self).order_by('-date')

    def is_public(self):
        if self.type == 1:
            return True
        else:
            return False

    def is_private(self):
        if self.type == 2:
            return True
        else:
            return False

    def is_active(self):
        if self.status == 1:
            return True
        else:
            return False

    def is_embigo_space(self):
        if self.uid == '00000000-0000-0000-0000-000000000000':
            return True
        else:
            return False


class SpaceUser(models.Model):
    class Meta:
        verbose_name = "użytkownik przestrzeni"
        verbose_name_plural = "użytkownicy przestrzeni"

    uid = models.CharField(primary_key=True, max_length=64)
    rights = models.CharField(max_length=32, null=True, blank=True)
    space = models.ForeignKey(Space, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return "%s z %s" % (self.user.username, self.space.name)

    def can(self, right):
        return int(self.rights[right])

    def setRights(self, rights):
        self.rights = rights

    def getRights(self):
        tab = []
        i = 0
        i = 0
        for c in self.rights:
            if len(tab) < 10:
                if (i != 2) & (i != 3):
                    if c == '1':
                        tab.append(True)
                    else:
                        tab.append(False)
            i = i + 1
        return tab


class Message(models.Model):
    class Meta:
        verbose_name = "komentarz"
        verbose_name_plural = "komentarze"

    uid = models.CharField(primary_key=True, max_length=64)
    content = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    space = models.ForeignKey(Space, null=True, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    file = models.FileField(upload_to='', null=True, blank=True)

    def get_date_for_message(self):
        sub = (timezone.localtime(timezone.now()) - self.date).days
        if sub == 0:
            return "Dzisiaj"
        elif sub == 1:
            return "Wczoraj"
        elif sub < 4:
            return str(sub) + " dni temu"
        else:
            return self.date

    def get_filepath(self):
        return settings.MEDIA_URL + self.file.name

    def check_if_image(self):
        name, extension = os.path.splitext(self.file.name)
        if extension == '.png' or extension == '.jpg' or extension == '.bmp':
            return True
        return False

    def __str__(self):
        return "%s" % (self.content)


class Conversation(models.Model):
    class Meta:
        verbose_name = "konwersacja"
        verbose_name_plural = "konwersacje"

    members = models.ManyToManyField(User)
    isgroup = models.BooleanField()
    name = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return "%i: %s" % (self.id, self.members.all())


class ChatMessage(models.Model):
    class Meta:
        verbose_name = "wiadomość czatu"
        verbose_name_plural = "wiadomości czatu"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s: %s" % (self.user.username, self.text)

# class Contacts(models.Model):
#     class Meta:
#         verbose_name = "kontakt"
#         verbose_name_plural = "kontakty"
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     users_list = models.OneToManyField(User, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return "%s - %s" % (self.user1.username, self.user2.username)
