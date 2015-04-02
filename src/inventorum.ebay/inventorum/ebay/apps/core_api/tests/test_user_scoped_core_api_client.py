# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D

from django.conf import settings
from inventorum.ebay.apps.core_api.tests import CoreApiTest
from inventorum.ebay.tests import StagingTestAccount

from inventorum.ebay.tests.testcases import APITestCase

from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient, CoreAPIClient
from mock import patch


log = logging.getLogger(__name__)


class TestUserScopedCoreAPIClient(APITestCase):

    def setUp(self):
        super(TestUserScopedCoreAPIClient, self).setUp()

        self.account_id = StagingTestAccount.ACCOUNT_ID
        self.user_id = StagingTestAccount.USER_ID

        self.subject = UserScopedCoreAPIClient(user_id=self.user_id, account_id=self.account_id)

    def test_default_headers(self):
        expected_version = settings.VERSION

        self.assertEqual(self.subject.default_headers, {
            "User-Agent": "inv-ebay/{version}".format(version=expected_version),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Inv-User": unicode(self.user_id),
            "X-Inv-Account": unicode(self.account_id)
        })

    @CoreApiTest.vcr.use_cassette("get_product_simple.json")
    def test_get_products_without_ebay_meta(self):
        core_product = self.subject.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID)

        self.assertEqual(core_product.id, StagingTestAccount.Products.SIMPLE_PRODUCT_ID)
        self.assertEqual(core_product.name, "XtC Advanced 2 LTD")
        self.assertEqual(core_product.description, "GIANT XtC 27.5\" Advanced Carbon")
        self.assertEqual(core_product.gross_price, D("1999.99"))
        self.assertEqual(core_product.stock, D("1000"))

    @CoreApiTest.vcr.use_cassette("get_product_with_ebay_meta.json")
    def test_get_product_with_ebay_meta(self):
        core_product = self.subject.get_product(StagingTestAccount.Products.PRODUCT_WITH_EBAY_META_ID)

        self.assertEqual(core_product.id, StagingTestAccount.Products.PRODUCT_WITH_EBAY_META_ID)
        # non-channeled name: FastRoad CoMax
        self.assertEqual(core_product.name, "eBay: FastRoad CoMax")
        # non-channeled description: GIANT FastRoad CoMax Carbon
        self.assertEqual(core_product.description, "eBay: GIANT FastRoad CoMax Carbon")
        # non-channeled gross price: 1999.99
        self.assertEqual(core_product.gross_price, D("1599.99"))
        self.assertEqual(core_product.stock, D("1000"))
