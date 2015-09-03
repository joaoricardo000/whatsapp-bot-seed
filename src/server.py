"""
    The server starter.

    It has all Yowsup core layers to handle the connection, encryption and media handling.
    https://github.com/tgalal/yowsup/wiki/Yowsup-2.0-Architecture

    The top layer of the stack is the RouteLayer (from route.py).
    It also imports the phone/whatsapp credentials from config.py
"""
from yowsup.layers import YowLayerEvent, YowParallelLayer
from yowsup.layers.auth import YowAuthenticationProtocolLayer, AuthError
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_messages import YowMessagesProtocolLayer
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_receipts import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks import YowAckProtocolLayer
from yowsup.layers.protocol_iq import YowIqProtocolLayer
from yowsup.layers.axolotl import YowAxolotlLayer
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS

from router import RouteLayer


class YowsupBotStack(object):
    def __init__(self, credentials):
        """Default Yowsup setup, with the Route Layer on top"""
        layers = (RouteLayer,
                  YowParallelLayer([YowAuthenticationProtocolLayer,
                                    YowMessagesProtocolLayer,
                                    YowReceiptProtocolLayer,
                                    YowAckProtocolLayer,
                                    YowMediaProtocolLayer,
                                    YowIqProtocolLayer]),
                  YowAxolotlLayer,
                  ) + YOWSUP_CORE_LAYERS
        self.stack = YowStack(layers)
        self.stack.setCredentials(credentials)

    def start(self):
        """Starts the connection with Whatsapp servers,"""
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            logging.info("Starting....")
            self.stack.loop()
        except AuthError as e:
            print("Authentication Error: %s" % e.message)


if __name__ == "__main__":
    import config
    import logging

    logging.basicConfig(level=logging.INFO)
    server = YowsupBotStack(config.auth) # Create a client with the credentials
    while True: # In case of disconnect, keeps connecting...
        server.start()