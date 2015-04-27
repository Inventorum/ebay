# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.notifications import EbayNotificationEventType, handlers, EbayNotificationStatus
from inventorum.ebay.apps.notifications.handlers import EbayNotificationHandlerException


log = logging.getLogger(__name__)


class EbayPlatformNotificationService(object):
    """
    Entry point for all ebay platform notifications, responsible for invoking the correct notification handlers
    """

    handlers = {
        EbayNotificationEventType.FixedPriceTransaction: handlers.FixedPriceTransactionNotificationHandler,
        EbayNotificationEventType.ItemSold: handlers.ItemSoldNotificationHandler,
        EbayNotificationEventType.ItemClosed: handlers.ItemClosedNotificationHandler,
        EbayNotificationEventType.ItemSuspended: handlers.ItemSuspendedNotificationHandler
    }

    @classmethod
    def handle(cls, notification):
        """
        :type notification: inventorum.ebay.apps.notifications.models.EbayNotificationModel
        """
        handler = cls._get_handler_for_event_type(notification.event_type, notification)
        if handler is None:
            notification.set_status(EbayNotificationStatus.UNHANDLED)
            return

        try:
            handler(notification)
        except EbayNotificationHandlerException as e:
            log.error("Error while handling %s notification with pk %s: %s",
                      notification.event_type, notification.pk, e.message)
            notification.set_status(EbayNotificationStatus.FAILED, details=e.message)
        else:
            notification.set_status(EbayNotificationStatus.HANDLED)

    @classmethod
    def _get_handler_for_event_type(cls, event_type, notification):
        """
        :type event_type: unicode
        :rtype: inventorum.ebay.apps.notifications.handlers.EbayNotificationHandler
        """
        handler_cls = cls.handlers.get(event_type, None)
        if handler_cls is None:
            return None

        return handler_cls()
