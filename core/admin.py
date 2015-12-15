from django.contrib import admin
from core.models import Space, SpaceUser, Message

admin.site.register(Space)
admin.site.register(SpaceUser)
admin.site.register(Message)