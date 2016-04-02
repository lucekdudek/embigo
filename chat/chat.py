from itertools import chain

from django.contrib.auth.models import User

from chat.connected_users import ConnectedUsers
from core.models import Conversation


YELLOW = '\033[93m'
ENDC = '\033[0m'

connected = ConnectedUsers()
last_update_time = -1


def print_color(string):
    print(YELLOW+str(string)+ENDC)


def send_list(server):  # TODO
    string = ';'.join(str(k.username) for (k, v) in connected.get_unique().items())
    for c in server.clients:
        server.send_message(c, "l;"+string)  # e.g. cu:root:test message


def get_or_create_conversation(user1, user2):
    if not isinstance(user1, User):
        user1 = User.objects.get(username=user1)
    if not isinstance(user2, User):
        user2 = User.objects.get(username=user2)

    conversations = Conversation.objects.filter(isgroup=False, members=user1)
    try:
        return conversations.get(members=user2)
    except Conversation.DoesNotExist:
        conv = Conversation(isgroup=False)
        conv.save()
        conv.members.add(user1)
        conv.members.add(user2)
        return conv
