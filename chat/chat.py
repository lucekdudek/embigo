from django.contrib.auth.models import User

from chat.connected_users import ConnectedUsers
from core.models import Conversation

YELLOW = '\033[93m'
ENDC = '\033[0m'

connected = ConnectedUsers()
last_update_time = -1


def print_color(string):
    print(YELLOW + str(string) + ENDC)


def send_online(server):  # TODO
    string = ';'.join(str(k.username) for (k, v) in connected.get_unique().items())
    for c in server.clients:
        server.send_message(c, "o;" + string)


def send_list(server, client, username):
    users_list = User.objects.filter(is_active=1).exclude(username=username).order_by('username')

    if not isinstance(username, User):
        username = User.objects.get(username=username)
    conversations = Conversation.objects.filter(isgroup=False, members=username)
    users_list = set()
    for conv in conversations:
        for user in conv.members.all().exclude(username=username):
            users_list.add(user.username)
    users_list = sorted(users_list, key=str.lower)
    print(conversations)

    list = "l"
    for x in users_list:
        list += ";" + str(get_or_create_conversation(username, x).id) + ";" + x
    server.send_message(client, list)


def send_group_list(server, client, username):
    if not isinstance(username, User):
        username = User.objects.get(username=username)
    conversations = Conversation.objects.filter(isgroup=True, members=username)

    conv_list = set()
    for conv in conversations:
        conv_list.add(conv)
    users_list = sorted(conv_list)

    list = "L"
    for x in users_list:
        list += ";" + str(x.id) + ";"
        for i, j in enumerate(x.members.all()):
            if i > 0:
                list += ", "+j.username
            else:
                list += j.username
    print(list)
    server.send_message(client, list)


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
