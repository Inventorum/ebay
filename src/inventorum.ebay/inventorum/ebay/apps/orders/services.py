# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.db import transaction
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemVariationModel
from inventorum.ebay.lib.ebay.data import OrderStatusCodeType
from inventorum.ebay.lib.ebay.data.events import EbayEventType, EbayEventReadyForPickup, EbayEventPickedUp, \
    EbayEventCanceled, CancellationType
from inventorum.ebay.lib.ebay.events import EbayInboundEvents
from inventorum.ebay.lib.ebay.orders import EbayOrders
from inventorum.ebay.lib.rest.serializers import POPOSerializer


log = logging.getLogger(__name__)


class CoreOrderService(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def create_in_core_api(self, order):
        """
        :type order: inventorum.ebay.apps.orders.models.OrderModel
        """
        data = OrderModelCoreAPIDataSerializer(order).data
        inv_id = self.account.core_api.create_order(data)

        order.inv_id = inv_id
        order.save()


class EbayOrderStatusUpdateException(Exception):
    pass


class EbayOrderStatusUpdateService(object):

    def __init__(self, account, order):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :type order: OrderModel
        """
        self.account = account
        self.order = order

    def regular_status_update(self):
        api = EbayOrders(self.account.token.ebay_object)
        api.complete_sale(order_id=self.order.ebay_id,
                          paid=self.order.core_status.is_paid,
                          shipped=self.order.core_status.is_shipped)

        # update succeeded => update ebay state
        self.order.ebay_status.is_paid = self.order.core_status.is_paid
        self.order.ebay_status.is_shipped = self.order.core_status.is_shipped
        self.order.ebay_status.save()

    def status_update_with_click_and_collect_event(self, event_type):
        """
        :type event_type: unicode
        """
        inbound_events = EbayInboundEvents(self.account.token.ebay_object)

        if event_type == EbayEventType.READY_FOR_PICKUP and not self.order.ebay_status.is_shipped:
            event = EbayEventReadyForPickup(order_id=self.order.ebay_id)
            inbound_events.publish(event, raise_exceptions=True)
            # update succeeded => update ebay state
            self.order.ebay_status.is_shipped = True
            self.order.ebay_status.save()
        elif event_type == EbayEventType.PICKED_UP and not self.order.ebay_status.is_closed:
            event = EbayEventPickedUp(order_id=self.order.ebay_id)
            inbound_events.publish(event, raise_exceptions=True)
            # update succeeded => update ebay state
            self.order.ebay_status.is_closed = True
            self.order.ebay_status.save()
        elif event_type == EbayEventType.CANCELED and not self.order.ebay_status.is_canceled:
            event = EbayEventCanceled(order_id=self.order.ebay_id, cancellation_type=CancellationType.OUT_OF_STOCK)
            inbound_events.publish(event, raise_exceptions=True)
            # update succeeded => update ebay state
            self.order.ebay_status.is_canceled = True
            self.order.ebay_status.save()
        else:
            raise EbayOrderStatusUpdateException("Got invalid or not supported event type `{}` for order {}"
                                                 .format(event_type, self.order))
