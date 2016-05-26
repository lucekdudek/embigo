# -*- coding: utf-8 -*-
import json
import logging
import threading
from itertools import chain

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from chat.chat import print_color, send_list, connected, send_online, get_or_create_conversation, send_group_list, \
    get_conv_name
from core.crypto import *
from core.models import ChatMessage, Conversation
from embigo.settings import WEBSOCKET_PORT

# Called for every client connecting (after handshake)
from websocket_server.websocket_server import WebsocketServer


def new_client(client, server):
    print_color("New client connected and was given id %d" % client['id'])


# Called for every client disconnecting
def client_left(client, server):
    if client is not None:
        try:
            connected.remove(client["id"])
            print_color("Client(%d) disconnected" % client['id'])
            send_online(server)
        except KeyError:
            logging.error("user doesn't exist")




def message_received(client, server, message):
    message = decode_utf_8(message)

    user = connected.get(client["id"])
    if user is not None:
        if message[0] == "m":
            message = message[2:]
            index = message.index(";")
            target = message[:index]
            message = message[(index + 1):]

            print_color("Client(%d) said: %s" % (client['id'], message))
            conversation = get_or_create_conversation(target, user)

            new_chat_message = ChatMessage(user=user, conversation=conversation, text=message)
            new_chat_message.save()
            for c in server.clients:
                if c['id'] != client['id']:
                    if connected.get(c['id']) == user:
                        x = 'cu'  # current user
                    else:
                        x = 'ou'  # other user
                    server.send_message(c, "m;" + str(
                        conversation.id) + ";" + user.username + ";" + message)  # e.g. cu:root:test message
        if (message[0] == "n") or (message[0] == "o"):
            param1 = message[2:]
            if user.username != param1:
                conversation = get_or_create_conversation(param1, user)
                chat_messages = ChatMessage.objects.filter(conversation=conversation)
                data = {}
                counter = 0
                for current_message in chat_messages:
                    data[counter] = "m;" + str(
                        conversation.id) + ";" + current_message.user.username + ";" + current_message.text
                    counter += 1
                if message[0] == "o":
                    send_list(server, client, user.username)
                    send_group_list(server, client, user.username)
                    send_online(server)
                    server.send_message(client, "w;" + message[2:] + ";" + str(get_or_create_conversation(message[2:], user).id) + ";" + User.objects.get(username=message[2:]).get_color())

                    u = User.objects.get(username=message[2:])
                    for x in connected.get_id(u):
                        client_temp = connected.get_client(x)
                        send_list(server, client_temp, u.username)
                        send_group_list(server, client_temp, u.username)
                if message[0] == "n":
                    server.send_message(client, "a;" + str(conversation.id) + ";" + json.dumps(data))
        if message[0] == "g":
            id = message[2:].split(";")[0]
            users_list = message[(3+len(id)):].split(";")

            conversation = Conversation.objects.get(id=id)
            if conversation.isgroup:
                new_members = User.objects.filter(username__in=users_list)
                conversation.members.add(*new_members)
                for u in conversation.members.all():
                    for x in connected.get_id(u):
                        client_temp = connected.get_client(x)
                        send_list(server, client_temp, u.username)
                        send_group_list(server, client_temp, u.username)
            else:
                new_members = (conversation.members.all() | User.objects.filter(username__in=users_list)).distinct()
                if len(new_members) > 2:
                    conv = Conversation(isgroup=True)
                    conv.save()
                    conv.members.add(*new_members)
                    for u in conv.members.all():
                        for x in connected.get_id(u):
                            client_temp = connected.get_client(x)
                            send_list(server, client_temp, u.username)
                            send_group_list(server, client_temp, u.username)
        if message[0] == "r":
            id = message[2:].split(";")[0]
            new_name = message[(3 + len(id)):]
            conv = get_or_create_conversation(id, user)
            if conv.isgroup:
                conv.name = new_name
                conv.save()
                for u in conv.members.all():
                    for x in connected.get_id(u):
                        client_temp = connected.get_client(x)
                        server.send_message(client_temp, "r;" + str(conv.id) + ";" + get_conv_name(conv))
                        send_list(server, client_temp, u.username)
                        send_group_list(server, client_temp, u.username)
                send_online(server)
    else:
        try:
            session_id = decrypt(SECRET_KEY_WEBSOCKET, message)
            session = Session.objects.get(pk=session_id)
            u = User.objects.get(id=session.get_decoded().get('_auth_user_id', None))
            connected.add(client, u)

            send_list(server, client, u.username)
            send_group_list(server, client, u.username)
            send_online(server)
            server.send_message(client, "u;" + u.username)
        except Session.DoesNotExist:
            logging.error("Error: user doesn't exist")


def start_server():
    server = WebsocketServer(WEBSOCKET_PORT, "0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    print_color("Running WebSocket server...")
    server.run_forever()


def start_thread():
    threading.Thread(target=start_server).start()
