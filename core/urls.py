# -*- coding: utf-8 -*-

from django.conf.urls import url
from core.views import index, space

urlpatterns = [
    url(r'^$', index),
    url(r'(?P<space_id>[0-9a-z-]+)/$', space),
]