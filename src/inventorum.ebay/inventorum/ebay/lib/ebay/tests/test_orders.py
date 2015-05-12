# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.lib.ebay.data.orders import CheckoutStatusType, PaymentMethodType
from inventorum.ebay.lib.ebay.orders import EbayOrders
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestEbayOrders(EbayAuthenticatedAPITestCase):
    def _get_order(self, order_id):
        api = EbayOrders(self.ebay_token)
        orders_response = api.get_orders({
            'OrderIDArray': {
                'OrderID': [order_id]
            }
        })

        return orders_response.orders[0]

    @EbayTest.use_cassette("full_test_for_changing_state_of_order.yaml")
    def test_changing_paid_shipped(self):
        """
        Explains connection and dependencies of OrderState and CheckoutState nicely!
        :return:
        """
        order_id = '261869293885-1616104762016'

        api = EbayOrders(self.ebay_token)
        api.revise_checkout_status(
            order_id=order_id,
            checkout_status=CheckoutStatusType.INCOMPLETE,
            payment_method_used=PaymentMethodType.BANK_TRANSFER
        )
        api.complete_sale(order_id=order_id, shipped=False, paid=False)

        order = self._get_order(order_id)
        self.assertEqual(order.checkout_status.status, "Incomplete")
        self.assertEqual(order.order_status, "Active")
        self.assertFalse(order.is_paid)
        self.assertFalse(order.is_shipped)

        api.revise_checkout_status(
            order_id=order_id,
            checkout_status=CheckoutStatusType.COMPLETE,
            payment_method_used=PaymentMethodType.BANK_TRANSFER
        )
        order = self._get_order(order_id)
        self.assertEqual(order.checkout_status.status, "Complete")
        self.assertEqual(order.order_status, "Completed")
        self.assertTrue(order.is_paid)  # When u say it is completed, is_paid is changed to TRUE cause u send used payment method!
        self.assertFalse(order.is_shipped)

        # However, you need to be carefull cause on ebay.de it is not marked as Paid

        api.complete_sale(order_id=order_id, shipped=True, paid=True)

        order = self._get_order(order_id)
        self.assertEqual(order.checkout_status.status, "Complete")
        self.assertEqual(order.order_status, "Completed")
        self.assertTrue(order.is_paid)
        self.assertTrue(order.is_shipped)
