import threading
import logging

from websocket_server import WebsocketServer
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    server.send_message_to_all("Hey all, a new client has joined us")

    # try:
    #     session = Session.objects.get(pk='14ngy0kxoqsj2doymys2xlw7o0ndj98w')
    #     user_name = User.objects.get(id=session.get_decoded().get('_auth_user_id', None))
    #     server.send_message(client, "zalogowany jako " + user_name.username)
    #     print(user_name)
    # except Session.DoesNotExist:
    #     logging.error("Error: user doesn't exist")

# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'
    print("Client(%d) said: %s" % (client['id'], message))
    try:
        session = Session.objects.get(pk=message)
        user_name = User.objects.get(id=session.get_decoded().get('_auth_user_id', None))
        server.send_message(client, "zalogowany jako " + user_name.username)
        print(user_name)
    except Session.DoesNotExist:
        logging.error("Error: user doesn't exist")


def start_server():
    PORT=9001
    server = WebsocketServer(PORT)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    print("start")
    server.run_forever()
    print("stop")

def start_thread():
    threading.Thread(target=start_server).start()