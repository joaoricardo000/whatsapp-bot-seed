"""
    This is the server starter.

    It has all Yowsup core layers to handle the connection, encryption and media handling.
    https://github.com/tgalal/yowsup/wiki/Yowsup-2.0-Architecture

    The top layer of the stack is the RouteLayer (from route.py).
"""
import logging, time, os, sys
from yowsup.layers import YowLayerEvent, YowParallelLayer
from yowsup.layers.auth import AuthError
from yowsup.layers.network import YowNetworkLayer
from yowsup.stacks.yowstack import YowStackBuilder

from layers.notifications.notification_layer import NotificationsLayer
from router import RouteLayer


class YowsupEchoStack(object):
    def __init__(self, credentials):
        "Creates the stacks of the Yowsup Server,"
        self.credentials = credentials
        stack_builder = YowStackBuilder().pushDefaultLayers(True)

        # on the top stack, the two layers that controls the bot and respond to messages and notifications
        # see both of classes for more documentation
        stack_builder.push(YowParallelLayer([RouteLayer, NotificationsLayer]))
        self.stack = stack_builder.build()
        self.stack.setCredentials(credentials)

    def start(self):
        "Starts the connection with Whatsapp servers,"
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            logging.info("#" * 50)
            logging.info("\tServer started. Phone number: %s" % self.credentials[0])
            logging.info("#" * 50)
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            logging.exception("Authentication Error: %s" % e.message)
            if "<xml-not-well-formed>" in str(e):
                os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            logging.exception("Unexpected Exception: %s" % e.message)


if __name__ == "__main__":
    import sys
    import config

    logging.basicConfig(stream=sys.stdout, level=config.logging_level, format=config.log_format)
    server = YowsupEchoStack(config.auth)
    while True:
        # In case of disconnect, keeps connecting...
        server.start()
        logging.info("Restarting..")
