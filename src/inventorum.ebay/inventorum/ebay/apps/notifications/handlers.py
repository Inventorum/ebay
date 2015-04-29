# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.products.models import EbayItemModel

from inventorum.ebay.lib.ebay.data.responses import GetItemTransactionsResponse, GetItemResponse
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
            raise EbayNotificationHandlerException("{exception}: {error}".format(exception=e.__class__.__name__,
                                                                                 error=str(e)))

    def handle(self, payload):
        """
        Handlers gonna handle!

        :param payload: The deserialized notification payload
        """
        raise NotImplementedError


class FixedPriceTransactionNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemTransactionsResponse.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemTransactionsResponse
        """
        # There should be exactly one as the GetItemTransactionsResponse is generated with the ItemID and TransactionID
        if len(payload.transactions) != 1:
            raise EbayNotificationHandlerException("Expected 1 but got %s transactions" % len(payload.transactions))

        transaction = payload.transactions[0]
        item = payload.item

        try:
            ebay_item_model = EbayItemModel.objects.get(external_id=item.item_id)
        except EbayItemModel.DoesNotExist as e:
            log.error("No EbayItemModel found with ebay item id {}".format(item.item_id))
            # We fail gracefully here as this happens when the account has other ebay listings not created with our tool
            return

        account = ebay_item_model.account

        # Since we do not support multiple line item orders (known as a Combined Invoice orders),
        # we can safely assume that the order_id is the ItemID and TransactionID, with a hyphen in between
        # See: http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetItemTransactions.html
        ebay_order_id = "%s-%s" % (item.item_id, transaction.transaction_id)

        order = OrderModel.objects.create(account=account,
                                          ebay_id=ebay_order_id,
                                          final_price=transaction.amount_paid,
                                          ebay_status=transaction.status.complete_status,
                                          created_from=self.notification)

        order.line_items.create(ebay_id=transaction.transaction_id,
                                orderable_item=ebay_item_model,
                                quantity=transaction.quantity_purchased,
                                unit_price=transaction.transaction_price)

        # schedule_order_creation_in_core_api(order.id)


class ItemSoldNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemResponse.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemResponse
        """
        pass


class ItemClosedNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemResponse.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemResponse
        """
        pass


class ItemSuspendedNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemResponse.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemResponse
        """
        pass
