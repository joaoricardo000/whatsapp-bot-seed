"""
    Basic views callbacks functions.

    Receives the message object and the regex match.
    If it returns a Message Entity, it will be sent back to origin (user or group)
"""
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity


def ping(message, match):
    return TextMessageProtocolEntity("Pong!", to=message.getFrom())


def echo(message, match):
    return TextMessageProtocolEntity("Eco: %s" % match.group("eco_message"), to=message.getFrom())
