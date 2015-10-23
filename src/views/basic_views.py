from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity


def echo(message, match):
    return TextMessageProtocolEntity("Echo: %s" % match.group("echo_message"), to=message.getFrom())


def ping(message, match):
    return TextMessageProtocolEntity("Pong!", to=message.getFrom())
