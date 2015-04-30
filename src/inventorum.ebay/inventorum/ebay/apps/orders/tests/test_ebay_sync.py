# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.tests import CoreApiTest, EbayTest, MockedTest
from inventorum.ebay.apps.orders.ebay_sync import EbayOrdersSync
from inventorum.ebay.tests.testcases import APITestCase, EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class IntegrationTestEbayOrdersSync(EbayAuthenticatedAPITestCase):

    @MockedTest.use_cassette("ebay_orders_sync.yaml")
    def test_ebay_orders_sync(self):
        syncer = EbayOrdersSync(account=self.account)
        syncer.run()
