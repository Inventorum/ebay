# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.notifications import EbayGetItemResponseDeserializer


log = logging.getLogger(__name__)


class EbayNotificationHandlerException(Exception):
    pass


class EbayNotificationHandler(object):
    """ Interface for ebay platform notification handlers """

    def handle(self, notification):
        """
        Handlers gonna handle!

        :type notification: inventorum.ebay.lib.ebay.notifications.EbayNotification
        """
        raise NotImplementedError

    def parse_payload(self, payload):
        """
        :type payload: dict
        """
        raise NotImplementedError


class ItemNotificationHandler(EbayNotificationHandler):
    """ Abstract base class for notifications with the GetItemResponse as payload """

    def parse_payload(self, payload):
        """
        :type payload: dict
        :rtype
        """
        pass


class FixedPriceTransactionNotificationHandler(EbayNotificationHandler):

    def handle(self, notification):
        """
        :type notification: inventorum.ebay.lib.ebay.notifications.EbayNotification
        """
        pass

    def parse_payload(self, payload):
        """
        :type payload: dict
        """
        pass


class ItemSoldNotificationHandler(ItemNotificationHandler):

    def handle(self, notification):
        """
        :type notification: inventorum.ebay.lib.ebay.notifications.EbayNotification
        """
        pass


class ItemClosedNotificationHandler(ItemNotificationHandler):

    def handle(self, notification):
        """
        :type notification: inventorum.ebay.lib.ebay.notifications.EbayNotification
        """
        pass


class ItemSuspendedNotificationHandler(ItemNotificationHandler):

    def handle(self, notification):
        """
        :type notification: inventorum.ebay.lib.ebay.notifications.EbayNotification
        """
        pass
