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

    list = "l"
    for x in users_list:
        user2 = User.objects.get(username=x)
        list += ";" + str(conversations.get(members=user2).id) + ";" + user2.get_color() + ";" + x
    server.send_message(client, list)


def get_conv_name(conversation):
    x = conversation

    list = ""

    if len(x.name) > 0:
        list += x.name + " ("
    for i, j in enumerate(x.members.all()):
        if i > 0:
            list += ", "+j.username
        else:
            list += j.username
    if len(x.name) > 0:
        list += ")"

    return list


def send_group_list(server, client, username):
    if not isinstance(username, User):
        username = User.objects.get(username=username)
    conversations = Conversation.objects.filter(isgroup=True, members=username)

    conv_list = set()
    for conv in conversations:
        conv_list.add(conv)
    # users_list = sorted(conv_list)
    users_list = conv_list

    list = "L"
    for x in users_list:
        list += ";" + str(x.id) + ";"

        if len(x.name) > 0:
            list += x.name + " ("
        for i, j in enumerate(x.members.all()):
            if i > 0:
                list += ", "+j.username
            else:
                list += j.username
        if len(x.name) > 0:
            list += ")"
    server.send_message(client, list)


def get_or_create_conversation(conv_id, user2):
    try:
        int(conv_id)
        return Conversation.objects.get(id=conv_id)
    except ValueError:
        user1 = User.objects.get(username=conv_id)
        try:
            return Conversation.objects.filter(isgroup=False, members=user2).get(members=user1)
        except Conversation.DoesNotExist:
            conv = Conversation(isgroup=False)
            conv.save()
            conv.members.add(user1)
            conv.members.add(user2)
            return conv
