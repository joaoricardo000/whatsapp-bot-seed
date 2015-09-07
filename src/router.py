"""
    The Route Layer.

    Here the message is routed to its proper view.
    The routes are defined with regular expressions and callback functions (just like any web framework).
"""

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback

import threading
import re

from views import basic_views
from views.downloads import MediaViews
from views.group_admin import GroupAdminViews


class RouteLayer(YowInterfaceLayer):
    def __init__(self):
        """
            The definition of routes and views (callbacks)!

            For the simple message handling, just calls the callback function, and expects a message entity to return.
            For more complex handling, like asynchronous file upload and sending, it creates a object passing 'self',
            so the callback can access the 'self.toLower' method
        """
        super(RouteLayer, self).__init__()

        routes = [("^/ping", basic_views.ping),
                  ("^/eco\s(?P<eco_message>[^$]+)", basic_views.echo), ]
        routes.extend(MediaViews(self).routes)  # Adds the auto download media routes
        routes.extend(GroupAdminViews(self).routes)

        self.views = [(re.compile(pattern), callback) for pattern, callback in routes]

    @ProtocolEntityCallback("message")
    def on_message(self, message):
        """Executes on every received message"""
        self.toLower(message.ack(True))  # Auto ack (double blue check symbol)
        # Routing only text type messages, for now ignoring other types. (media, audio, location...)
        if message.getType() == 'text':
            # Route the message on a new thread to not block the others messages (probably needs performance enhance)
            threading.Thread(target=self.route, args=(message,)).start()

    def route(self, message):
        """Get the text from message and tests on every route for a match"""
        text = message.getBody()
        for route, callback in self.views:
            match = route.match(text)
            if match:  # in case of regex match, the callback is called, passing the message and the match object
                data = callback(message, match)
                if data: self.toLower(data)  # if callback returns a message entity, sends it.
                break

    @ProtocolEntityCallback("receipt")
    def on_receipt(self, entity):
        """Auto ack for every message receipt confirmation"""
        self.toLower(entity.ack())
