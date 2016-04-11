# -*- coding: utf-8 -*-
import json
import threading
import logging

from chat.chat import print_color, send_list, connected, send_online, get_or_create_conversation
from core.models import ChatMessage, Conversation
from embigo.settings import WEBSOCKET_PORT
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from core.crypto import *

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


# Called when a client sends a message
def message_received(client, server, message):
    message = decode_utf_8(message)

    user = connected.get(client["id"])
    if user is not None:
        if message[0] == "m":
            message = message[2:]
            index = message.index(";")
            target = message[:index]
            message = message[(index+1):]

            print_color("Client(%d) said: %s" % (client['id'], message))
            conversation = get_or_create_conversation(user, target)

            new_chat_message = ChatMessage(user=user, conversation=conversation, text=message)
            new_chat_message.save()
            for c in server.clients:
                if c['id'] != client['id']:
                    print(connected.get(c['id']))
                    if connected.get(c['id']) == user:
                        x = 'cu'  # current user
                    else:
                        x = 'ou'  # other user
                    server.send_message(c, "m;" + str(conversation.id) + ";" + user.username + ";" + message)  # e.g. cu:root:test message
        if message[0] == "n":
            message = message[2:]
            conversation = get_or_create_conversation(user, message)
            chat_messages = ChatMessage.objects.filter(conversation=conversation)
            data = {}
            counter=0
            for current_message in chat_messages:
                data[counter] = "m;" + str(conversation.id) + ";" + current_message.user.username + ";" + current_message.text
                counter += 1
            server.send_message(client, "a;"+str(conversation.id)+";"+json.dumps(data))
    else:
        try:
            session_id = decrypt(SECRET_KEY_WEBSOCKET, message)
            session = Session.objects.get(pk=session_id)
            u=User.objects.get(id=session.get_decoded().get('_auth_user_id', None))
            connected.add(client['id'], u)

            send_list(server, client, u.username)
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
