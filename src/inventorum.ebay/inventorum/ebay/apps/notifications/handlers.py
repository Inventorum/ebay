# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.translation import ugettext
from inventorum.ebay.apps.orders.tasks import schedule_ebay_orders_sync

from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.apps.products.tasks import schedule_core_api_publishing_status_update

from inventorum.ebay.lib.ebay.data.responses import GetItemTransactionsResponseType, GetItemResponseType
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from inventorum.util.celery import TaskExecutionContext
from inventorum.util.django.middlewares import get_current_request_id
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
                                                                                 error=unicode(e)))

    def handle(self, payload):
        """
        Handlers gonna handle!

        :param payload: The deserialized notification payload
        """
        raise NotImplementedError


class FixedPriceTransactionNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemTransactionsResponseType.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemTransactionsResponseType
        """
        item_id = payload.item.item_id

        try:
            item = EbayItemModel.objects.by_ebay_id(item_id).get()
        except EbayItemModel.DoesNotExist:
            # wasn't ours, ignore
            return

        log.info("Handling FixedPriceTransaction notification for ebay item {}".format(item_id))

        account = item.account
        schedule_ebay_orders_sync(account_id=account.id,
                                  context=TaskExecutionContext(account_id=account.id,
                                                               user_id=account.default_user.id,
                                                               request_id=get_current_request_id()))


class ItemSoldNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemResponseType.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemResponseType
        """
        item_id = payload.item.item_id

        try:
            item = EbayItemModel.objects.by_ebay_id(item_id).get()
        except EbayItemModel.DoesNotExist:
            # wasn't ours, ignore
            return

        log.info("Handling ItemSold notification for ebay item {}".format(item_id))

        account = item.account
        schedule_ebay_orders_sync(account_id=account.id,
                                  context=TaskExecutionContext(account_id=account.id,
                                                               user_id=account.default_user.id,
                                                               request_id=get_current_request_id()))


class ItemClosedNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemResponseType.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemResponseType
        """
        item_id = payload.item.item_id

        try:
            item = EbayItemModel.objects.by_ebay_id(item_id).get()
        except EbayItemModel.DoesNotExist:
            # wasn't ours, ignore
            return

        if item.publishing_status != EbayItemPublishingStatus.UNPUBLISHED:
            log.info("Handling ItemClosed notification for ebay item {}".format(item_id))

            item.set_publishing_status(EbayItemPublishingStatus.UNPUBLISHED)

            account = item.account
            schedule_core_api_publishing_status_update(ebay_item_id=item.id,
                                                       context=TaskExecutionContext(account_id=account.id,
                                                                                    user_id=account.default_user.id,
                                                                                    request_id=get_current_request_id()))
        else:
            log.info("Got ItemClosed notification for already unpublished ebay item {}".format(item_id))


class ItemSuspendedNotificationHandler(EbayNotificationHandler):
    payload_deserializer_class = GetItemResponseType.Deserializer

    def handle(self, payload):
        """
        :type payload: inventorum.ebay.lib.ebay.data.responses.GetItemResponseType
        """
        item_id = payload.item.item_id

        try:
            item = EbayItemModel.objects.by_ebay_id(item_id).get()
        except EbayItemModel.DoesNotExist:
            # wasn't ours, ignore
            return

        log.info("Handling ItemSuspended notification for ebay item {}".format(item_id))

        item.set_publishing_status(EbayItemPublishingStatus.FAILED,
                                   [ugettext("The listing was suspended by ebay. "
                                             "Further details are available via the ebay website.")])

        account = item.account
        schedule_core_api_publishing_status_update(ebay_item_id=item.id,
                                                   context=TaskExecutionContext(account_id=account.id,
                                                                                user_id=account.default_user.id,
                                                                                request_id=get_current_request_id()))
