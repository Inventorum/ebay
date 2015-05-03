# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.db import transaction
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemVariationModel
from inventorum.ebay.lib.ebay.data import OrderStatusCodeType
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
