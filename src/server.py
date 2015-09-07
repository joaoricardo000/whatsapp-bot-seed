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
from yowsup.layers.protocol_groups.layer import YowGroupsProtocolLayer
from yowsup.layers.protocol_messages import YowMessagesProtocolLayer
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_receipts import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks import YowAckProtocolLayer
from yowsup.layers.protocol_iq import YowIqProtocolLayer
from yowsup.layers.axolotl import YowAxolotlLayer
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS

from router import RouteLayer
import logging


class YowsupBotStack(object):
    def __init__(self, credentials):
        """Default Yowsup setup, with the Route Layer on top"""
        layers = (RouteLayer,
                  YowParallelLayer([YowAuthenticationProtocolLayer,
                                    YowGroupsProtocolLayer,
                                    YowMessagesProtocolLayer,
                                    YowReceiptProtocolLayer,
                                    YowAckProtocolLayer,
                                    YowMediaProtocolLayer,
                                    YowIqProtocolLayer]),
                  YowAxolotlLayer,
                  ) + YOWSUP_CORE_LAYERS
        self.stack = YowStack(layers)
        self.stack.setCredentials(credentials)
        self.credentials = credentials

    def start(self):
        "Starts the connection with Whatsapp servers,"
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            logging.info("#" * 50)
            logging.info("Server started. Phone number: %s" % self.credentials[0])
            logging.info("#" * 50)
            self.stack.loop()
        except AuthError as e:
            logging.exception("Authentication Error: %s" % e.message)
        except Exception as e:
            logging.exception("Unknown Error: %s" % e.message)
            raise e


if __name__ == "__main__":
    import sys
    import config

    logging.basicConfig(stream=sys.stdout, level=config.logging_level, format=config.log_format)
    server = YowsupBotStack(config.auth)
    while True:
        # In case of disconnect, keeps connecting...
        server.start()
        logging.info("Restarting..")
