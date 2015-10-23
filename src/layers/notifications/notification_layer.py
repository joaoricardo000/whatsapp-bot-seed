"""
    This layers only respond to whatsapp server notifications.
    Notifications can be a inform that the bot was added in a group, or someone was added to a group, or anything like that.
    Check yowsup.layers.protocol_groups.protocolentities for all notification protocol objects in Yowsup.

    Is this implementation we use the CreateGroupsNotificationProtocolEntity to check if the bot was
    added in a group, and leave if it is not allowed.
"""
import config
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_groups.protocolentities.iq_groups_leave import LeaveGroupsIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.iq_result_groups_list import ListGroupsResultIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_add import AddGroupsNotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_create import \
    CreateGroupsNotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_remove import \
    RemoveGroupsNotificationProtocolEntity


class NotificationsLayer(YowInterfaceLayer):
    def __init__(self):
        super(NotificationsLayer, self).__init__()

    @ProtocolEntityCallback("notification")
    def onNotification(self, notification):
        """
            Reacts to any notification received
        """
        self.toLower(notification.ack())
        if isinstance(notification, CreateGroupsNotificationProtocolEntity):  # added on new group
            self.on_created_group(notification)
        elif isinstance(notification, ListGroupsResultIqProtocolEntity):  # result of a query of all groups
            self.on_groups_list(notification)
            # elif isinstance(notification, RemoveGroupsNotificationProtocolEntity):
            #     pass
            # elif isinstance(notification, AddGroupsNotificationProtocolEntity):
            #     pass

    def on_groups_list(self, listGroupResultEntity):
        groups = listGroupResultEntity.getGroups()
        for g in groups:
            if not self.is_allowed_on_group(g):
                self.leave_group(g)

    def on_created_group(self, createGroupsNotificationProtocolEntity):
        group_id = createGroupsNotificationProtocolEntity.getGroupId() + "@g.us"
        if self.is_allowed_on_group(createGroupsNotificationProtocolEntity):
            # this is a good place to a "Hello Group" message
            pass
        else:
            self.toLower(LeaveGroupsIqProtocolEntity(group_id))

    def is_allowed_on_group(self, group_entity):
        if config.filter_groups:
            isAllowed = False
            for jid, isAdmin in group_entity.getParticipants().iteritems():
                if jid.split("@")[0] in config.admins:
                    isAllowed = True
                    break
        else:
            isAllowed = True
        return isAllowed

    def leave_group(self, group_entity):
        group_id = group_entity.getGroupId() + "@g.us"
        self.toLower(LeaveGroupsIqProtocolEntity(group_id))


"""
##  Removed

notification
<class 'yowsup.layers.protocol_groups.protocolentities.notification_groups_remove.RemoveGroupsNotificationProtocolEntity'>
{'_type': 'w:gp2', 'timestamp': 1443379571, '_participant': '554896270570@s.whatsapp.net', 'participants': {'554898607439@s.whatsapp.net': None}, 'tag': 'notification', 'notify': 'Jo\xc3\xa3o Ricardo', '_from': '554896270570-1443068696@g.us', '_id': '554896270570-1443068696@g.us', 'offline': False, 'subject': 'kick admin'}

##  Added

notification
<class 'yowsup.layers.protocol_groups.protocolentities.notification_groups_create.CreateGroupsNotificationProtocolEntity'>
{'subjectTime': 1443068696, '_type': 'w:gp2', 'createType': None, 'timestamp': 1443379650, 'creatorJid': '554896270570@s.whatsapp.net', '_participant': '554896270570@s.whatsapp.net', 'groupId': '554896270570-1443068696', 'participants': {'554896270570@s.whatsapp.net': 'admin', '554898607439@s.whatsapp.net': None}, 'tag': 'notification', 'notify': 'Jo\xc3\xa3o Ricardo', 'subjectOwnerJid': '554896270570@s.whatsapp.net', '_from': '554896270570-1443068696@g.us', '_id': '554896270570-1443068696@g.us', 'creationTimestamp': 1443068696, 'offline': False, 'subject': 'kick admin'}

##  Member added

notification
<class 'yowsup.layers.protocol_groups.protocolentities.notification_groups_add.AddGroupsNotificationProtocolEntity'>
{'_type': 'w:gp2', 'timestamp': 1443379735, '_participant': '554896270570@s.whatsapp.net', 'participants': ['554898050168@s.whatsapp.net'], 'tag': 'notification', 'notify': 'Jo\xc3\xa3o Ricardo', '_from': '554896270570-1443068696@g.us', '_id': '554896270570-1443068696@g.us', 'offline': False}

## Member removed

notification
<class 'yowsup.layers.protocol_groups.protocolentities.notification_groups_remove.RemoveGroupsNotificationProtocolEntity'>
{'_type': 'w:gp2', 'timestamp': 1443380969, '_participant': '554896270570@s.whatsapp.net', 'participants': {'554899914159@s.whatsapp.net': None}, 'tag': 'notification', 'notify': 'Jo\xc3\xa3o Ricardo', '_from': '554896270570-1443068696@g.us', '_id': '554896270570-1443068696@g.us', 'offline': False, 'subject': 'kick admin'}
"""
