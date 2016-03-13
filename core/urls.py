# -*- coding: utf-8 -*-

from django.conf.urls import url
from core.views import index, space, signout, signin, register, new_message, delete_message, new_space, edit_space, \
    delete_space, archive_space, add_collaborators

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^00000000-0000-0000-0000-000000000000/$', index, name="index"),
    url(r'^in/$', signin, name="signin"),
    url(r'^out/$', signout, name="signout"),
    url(r'^register/$', register, name="register"),
    url(r'^new_message/$', new_message, name="new_message"),
    url(r'^delete_message/$', delete_message, name="delete_message"),
    url(r'^new_space/$', new_space, name="new_space"),
    url(r'^new_conversation/$', new_space, name="new_conversation"),
    url(r'^edit_space/$', edit_space, name="edit_space"),
    url(r'^add_collaborators/$', add_collaborators, name="add_collaborators"),
    url(r'(?P<space_id>[0-9a-z-]+)/$', space, name="space"),
    url(r'(?P<space_id>[0-9a-z-]+)/delete_space/1$', delete_space, name="delete_space"),
    url(r'(?P<space_id>[0-9a-z-]+)/archive_space/1$', archive_space, name="archive_space"),
]
