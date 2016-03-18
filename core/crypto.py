# -*- coding: utf-8 -*-
import base64

SECRET_KEY_WEBSOCKET = "password"

def encrypt(key, text):
    tab = bytearray(len(text))
    for i in range(len(text)):
        number = ord(text[i]) ^ ord(key[i%len(key)])
        tab[i] = number
    return base64.b64encode(tab)


def decrypt(key, text):
    tab = base64.b64decode(text)
    value = ""
    for i in range(len(tab)):
        number = tab[i] ^ ord(key[i%len(key)])
        value += chr(number)
    return value

def decode_utf_8(data):
    tab = bytearray(len(data))
    for i in range(len(data)):
        tab[i] = ord(data[i])
    return tab.decode("utf-8")