# -*- coding: utf-8 -*-

from django.conf.urls import url
from core.views import index, space, signout, signin, register, new_message, delete_message, new_space, edit_space, new_channel, \
    delete_space, enter_channel

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^in/$', signin, name="signin"),
    url(r'^out/$', signout, name="signout"),
    url(r'^register/$', register, name="register"),
    url(r'^new_message/$', new_message, name="new_message"),
    url(r'^delete_message/$', delete_message, name="delete_message"),
    url(r'^new_space/$', new_space, name="new_space"),
    url(r'^delete_space/$', delete_space, name="delete_space"),
    url(r'^new_conversation/$', new_space, name="new_conversation"),
    url(r'^edit_space/$', edit_space, name="edit_space"),
    url(r'^new_channel/$', new_channel, name="new_channel"),
    url(r'^enter_channel/$', enter_channel, name="enter_channel"),
    url(r'(?P<space_id>[0-9a-z-]+)/$', space, name="space"),
]
