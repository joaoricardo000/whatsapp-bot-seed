from threading import Timer
from yowsup.layers.protocol_groups.protocolentities.iq_groups_participants_add import AddParticipantsIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.iq_groups_participants_remove import \
    RemoveParticipantsIqProtocolEntity
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity


class GroupAdminViews():
    """
        Group Administration Views

        If the bot have admin privileges on the group, it will be able to
        add/remove participants.
    """

    def __init__(self, interface_layer):
        self.interface_layer = interface_layer
        self.routes = [
            # Kick with optional time parameter in seconds
            ("^/kick\s(?P<phone_number>[0-9]{8,14})\s*(?P<time>[0-9]{2,3})?\s*$", self.kick),
            ("^/add\s(?P<phone_number>[0-9]{8,14})\s*$", self.add),
            ("^/ban\s(?P<phone_number>[0-9]{8,14})\s*$", self.ban),
        ]

    def kick(self, message, match):
        """
            Kicks user from group and add back in <time> seconds. Default time is 15
        """
        if self._is_authorized(message):
            jid_kick = self._get_jid(match.group("phone_number"))
            self._remove_user(message.getFrom(), jid_kick)
            kick_duration = int(match.group("time")) if match.group("time") else 15
            Timer(kick_duration, self._add_user, (message.getFrom(), jid_kick)).start()
            notify_message = "{ %s foi kickado por %d segundos }" % (match.group("phone_number"), kick_duration)
            self.interface_layer.toLower(TextMessageProtocolEntity(notify_message, to=message.getFrom()))

    def add(self, message, match):
        """
            Adds user from group and add back in <time> seconds. Default time is 15
        """
        if self._is_authorized(message):
            jid_kick = self._get_jid(match.group("phone_number"))
            self._add_user(message.getFrom(), jid_kick)

    def ban(self, message, match):
        """
            Remover user from group and not add back
        """
        if self._is_authorized(message):
            jid_kick = self._get_jid(match.group("phone_number"))
            self._remove_user(message.getFrom(), jid_kick)

    def _is_authorized(self, message):
        """
            Check if bot is authorized to add/remove users.
            For now just checks if the message is in group,
            # TO-DO: check if bot is in fact admin!
            # issue:
        """
        return message.isGroupMessage()

    def _get_jid(self, phone_number):
        """
            Build jid based on phone number.
        """
        return "%s@s.whatsapp.net" % phone_number

    def _remove_user(self, group_jid, user_jid):
        """
            Create Remove entity and sends
        """
        entity = RemoveParticipantsIqProtocolEntity(group_jid, [user_jid, ])
        self.interface_layer.toLower(entity)

    def _add_user(self, group_jid, user_jid):
        """
            Create Add entity and sends
        """
        entity = AddParticipantsIqProtocolEntity(group_jid, [user_jid, ])
        self.interface_layer.toLower(entity)
