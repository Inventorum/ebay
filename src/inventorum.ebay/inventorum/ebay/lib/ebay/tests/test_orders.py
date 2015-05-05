# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.core_api.tests import MockedTest
from inventorum.ebay.lib.ebay.orders import EbayOrders
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestEbayOrders(EbayAuthenticatedAPITestCase):
    def test_complete_sale(self):
        api = EbayOrders(self.ebay_token)

        with MockedTest.use_cassette('ebay_complete_sale.yaml') as cass:
            api.complete_sale(order_id='261869293885-1616104762016', shipped=True)

        request = cass.requests[0]