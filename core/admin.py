from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from core.models import EmbigoUser, Space, SpaceUser, Message, Conversation, ChatMessage



class EmbigoUserInLine(admin.StackedInline):
    model = EmbigoUser
    can_delete = False


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EmbigoUserInLine,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# admin.site.register(EmbigoUser)
admin.site.register(Space)
admin.site.register(SpaceUser)

admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(ChatMessage)


