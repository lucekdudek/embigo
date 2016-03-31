from itertools import chain

from django.contrib.auth.models import User

from core.models import Conversation


YELLOW = '\033[93m'
ENDC = '\033[0m'

connected_users = {}


def print_color(string):
    print(YELLOW+str(string)+ENDC)


def get_connected_users():
    unique_values = set(connected_users[d] for d in connected_users)
    print(unique_values)
    return unique_values


def is_online(user):
    for d in connected_users:
        if connected_users[d].username == user:
            return True
    return False


def send_list(server):# TODO
    lista = get_connected_users()

    string = ';'.join(str(e) for e in get_connected_users())
    print(string)

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