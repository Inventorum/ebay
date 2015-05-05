# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data.responses import GetOrdersResponseType


log = logging.getLogger(__name__)


class EbayOrders(EbayTrading):

    def get_orders(self, data):
        """
        http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetOrders.html

        :type data: dict
        :rtype: inventorum.ebay.lib.ebay.data.responses.GetOrdersResponseType
        """
        response = self.execute("GetOrders", data)
        return GetOrdersResponseType.Deserializer(data=response).build()

    def complete_sale(self, order_id, shipped, shipment=None):
        """
        http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/CompleteSale.html

        :type order_id: unicode
        :type shipped: bool
        :type shipment: inventorum.ebay.lib.ebay.data.orders.EbayCompleteSaleShipment
        """
        data = {
            'OrderID': order_id,
            'Shipped': shipped
        }
        if shipment is not None:
            data['Shipment'] = shipment.dict()

        response = self.execute('CompleteSale', data)
        # If something would go wrong, then we would get exception
        return True