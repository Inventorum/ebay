# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.data.notifications import EbayGetItemTransactionsResponseDeserializer, \
    EbayGetItemResponseDeserializer
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


class EbayNotificationHandlerException(Exception):
    pass


class EbayNotificationHandler(object):
    """ Interface for ebay platform notification handlers """
    payload_deserializer_class = None

    def __call__(self, notification):
        self.notification = notification
        payload = self._deserialize_payload(notification.payload)
        self.handle(payload)

    def _deserialize_payload(self, payload):
        payload_deserializer_class = self.payload_deserializer_class

        if payload_deserializer_class is None:
            raise Exception("`payload_serializer_class` must be defined for %s" % self.__class__.__name__)

        if not issubclass(payload_deserializer_class, POPOSerializer):
            raise Exception("`payload_serializer_class` must be instance of %s" % POPOSerializer.__name__)

        try:
            return payload_deserializer_class(data=payload).build()
        except ValidationError as e:
            raise EbayNotificationHandlerException("Cannot deserialize payload: %s" % e.detail)

    def handle(self, payload):
        """
        Handlers gonna handle!

        :param payload: The deserialized notification payload
        """
        raise NotImplementedError


class FixedPriceTransactionNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = EbayGetItemTransactionsResponseDeserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.notifications.EbayGetItemTransactionsResponse
        """
        pass


class ItemSoldNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = EbayGetItemResponseDeserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.notifications.EbayGetItemResponse
        """
        pass


class ItemClosedNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = EbayGetItemResponseDeserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.notifications.EbayGetItemResponse
        """
        pass


class ItemSuspendedNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = EbayGetItemResponseDeserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.notifications.EbayGetItemResponse
        """
        pass
