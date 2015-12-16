# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

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

class Message(models.Model):
    class Meta():
        verbose_name = "komentarz"
        verbose_name_plural = "komentarze"
    uid = models.CharField(primary_key=True, max_length=64)
    content = models.CharField(max_length=255, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    space = models.ForeignKey(Space, null=True, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    def __str__(self):
        return "%s"%(self.content)
