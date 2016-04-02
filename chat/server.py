# -*- coding: utf-8 -*-
import threading
import logging

import time

from chat.chat import print_color, send_list, connected
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
            send_list(server)
        except KeyError:
            logging.error("user doesn't exist")


# Called when a client sends a message
def message_received(client, server, message):
    message = decode_utf_8(message)

    user = connected.get(client["id"])
    if user is not None:
        print_color("Client(%d) said: %s" % (client['id'], message))
        conversation = Conversation.objects.get(id=1)

        new_chat_message = ChatMessage(user=user, conversation=conversation, text=message)
        new_chat_message.save()
        for c in server.clients:
            if c['id'] != client['id']:
                if connected.get(c['id']) == user:
                    x = 'cu'  # current user
                else:
                    x = 'ou'  # other user
                server.send_message(c, x + ";" + user.username + ";" + message)  # e.g. cu:root:test message
    else:
        try:
            session_id = decrypt(SECRET_KEY_WEBSOCKET, message)
            session = Session.objects.get(pk=session_id)
            connected.add(client['id'], User.objects.get(id=session.get_decoded().get('_auth_user_id', None)))
            send_list(server)
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
