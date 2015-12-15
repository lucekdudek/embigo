# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Space(models.Model):
    uid = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

class SpaceUser(models.Model):
    uid = models.CharField(primary_key=True, max_length=64)
    rights = models.CharField(max_length=32, null=True, blank=True)
    space = models.ForeignKey(Space, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)

class Message(models.Model):
    uid = models.CharField(primary_key=True, max_length=64)
    content = models.CharField(max_length=255, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    space = models.ForeignKey(Space, null=True, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
