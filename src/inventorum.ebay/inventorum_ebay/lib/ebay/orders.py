# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.lib.ebay import EbayTrading
from inventorum_ebay.lib.ebay.data.responses import GetOrdersResponseType


log = logging.getLogger(__name__)


class EbayOrders(EbayTrading):

    def get_orders(self, data):
        """
        http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetOrders.html

        :type data: dict
        :rtype: inventorum_ebay.lib.ebay.data.responses.GetOrdersResponseType
        """
        response = self.execute("GetOrders", data)
        return GetOrdersResponseType.Deserializer(data=response).build()

    def complete_sale(self, order_id, shipped, paid, shipment=None):
        """
        http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/CompleteSale.html

        :type order_id: unicode
        :type shipped: bool
        :type shipment: inventorum_ebay.lib.ebay.data.orders.EbayCompleteSaleShipment
        """
        data = {
            'OrderID': order_id,
            'Shipped': shipped,
            'Paid': paid,
        }
        if shipment is not None:
            data['Shipment'] = shipment.dict()

        self.execute('CompleteSale', data)

    def revise_checkout_status(self, order_id, checkout_status, payment_method_used):
        """
        http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/ReviseCheckoutStatus.html
        :param checkout_status: Use CheckoutStatusType to determine status
        :param payment_method_used: Use PaymentMethodType to determine payment method
        :type order_id: unicode
        """
        self.execute('ReviseCheckoutStatus', {
            'OrderID': order_id,
            'CheckoutStatus': checkout_status,
            'PaymentMethodUsed': payment_method_used

        })
