# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone, formats
import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import os.path

class EmbigoUser(models.Model):
    class Meta():
        verbose_name = "użytkownik embigo"
        verbose_name_plural = "użytkownicy embigo"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, null=True, blank=True)
    def __str__(self):
        return "%s"%(self.user.username)

def get_color(self):
    try:
        color = self.embigouser.color
    except ObjectDoesNotExist:
        embigo_user = EmbigoUser(user=self, color="#FFFFFF")
        embigo_user.save()
        color = self.embigouser.color
    return color

User.add_to_class('get_color', get_color)

class Space(models.Model):
    class Meta():
        verbose_name = "przestrzeń"
        verbose_name_plural = "przestrzenie"
    uid = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    def __str__(self):
        return "%s"%(self.name)

    def get_path(self):
        paths = []
        parent=self.parent
        while parent!=None:
            paths.append(parent)
            parent=parent.parent
        return paths[::-1]

class SpaceUser(models.Model):
    class Meta():
        verbose_name = "użytkownik przestrzeni"
        verbose_name_plural = "użytkownicy przestrzeni"
    uid = models.CharField(primary_key=True, max_length=64)
    rights = models.CharField(max_length=32, null=True, blank=True)
    space = models.ForeignKey(Space, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return "%s z %s"%(self.user.username, self.space.name)

    def can(self, right):
        return int(self.rights[right])

class Message(models.Model):
    class Meta():
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
            return str(sub)+" dni temu"
        else:
            return self.date

    def get_filepath(self):
        return settings.MEDIA_URL+self.file.name

    def check_if_image(self):
        name, extension = os.path.splitext(self.file.name)
        if extension == '.png' or extension == '.jpg' or extension == '.bmp':
            return True
        return False

    def __str__(self):
        return "%s"%(self.content)
