# -*- coding: utf-8 -*-
import threading
import logging

from core.models import ChatMessage, Conversation
from websocket_server import WebsocketServer
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from core.crypto import *

connected_users = {}


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])


# Called for every client disconnecting
def client_left(client, server):
    if client is not None:
        try:
            del connected_users[client['id']]
            print("Client(%d) disconnected" % client['id'])
        except KeyError:
            logging.error("user doesn't exist")


# Called when a client sends a message
def message_received(client, server, message):
    message = decode_utf_8(message)

    if client['id'] in connected_users:
        print("Client(%d) said: %s" % (client['id'], message))
        conversation = Conversation.objects.get(id=1)
        user = User.objects.get(username=connected_users[client['id']])
        new_chat_message = ChatMessage(user=user, conversation=conversation, text=message)
        new_chat_message.save()
        for c in server.clients:
            if c['id'] != client['id']:
                server.send_message(c, message)
                # server.send_message(c, connected_users[client['id']] + " said: " + message)
    else:
        try:
            session_id = decrypt(SECRET_KEY_WEBSOCKET, message)
            session = Session.objects.get(pk=session_id)
            user_name = User.objects.get(id=session.get_decoded().get('_auth_user_id', None))
            # server.send_message(client, "zalogowany jako " + user_name.username)
            connected_users[client['id']] = user_name.username
            print(connected_users)
            print(server.clients)
        except Session.DoesNotExist:
            logging.error("Error: user doesn't exist")


def start_server():
    PORT = 9001
    server = WebsocketServer(PORT, "0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    print("start")
    server.run_forever()
    print("stop")


def start_thread():
    threading.Thread(target=start_server).start()
