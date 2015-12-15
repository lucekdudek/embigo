# -*- coding: utf-8 -*-

from django.conf.urls import url
from core.views import index, space, signout, signin, register

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^in/$', signin, name="signin"),
    url(r'^out/$', signout, name="signout"),
    url(r'^register/$', register, name="register"),
    url(r'(?P<space_id>[0-9a-z-]+)/$', space, name="space"),
]
