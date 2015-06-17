# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
import grequests
from decimal import Decimal
from inventorum.ebay import settings
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.models import EbayProductModel

from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.tests.live_server_test import ConcurrentLiveServerTestCase, ThreadedCoreAPIFake
from inventorum.ebay.tests.utils import JSONFixture, PatchMixin
from rest_framework import status


log = logging.getLogger(__name__)


class TestPublishingLocks(ConcurrentLiveServerTestCase, ProductTestMixin, PatchMixin, ShippingServiceTestMixin):
    TEST_CORE_API_HOST = "localhost:9999"

    @classmethod
    def setUpClass(cls):
        # change django settings for this particular test case
        cls.ORIGINAL_INV_CORE_API_HOST = settings.INV_CORE_API_HOST
        settings.INV_CORE_API_HOST = cls.TEST_CORE_API_HOST

        # start core api fake server
        host, port = cls.TEST_CORE_API_HOST.split(":")
        cls.threaded_core_api_fake = ThreadedCoreAPIFake(host=host, port=int(port))
        cls.threaded_core_api_fake.daemon = True
        cls.threaded_core_api_fake.start()
        super(TestPublishingLocks, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # reset django settings
        settings.INV_CORE_API_HOST = cls.ORIGINAL_INV_CORE_API_HOST

        # stop core api fake server
        cls.threaded_core_api_fake.stop()
        cls.threaded_core_api_fake.join()

        super(TestPublishingLocks, cls).tearDownClass()

    def test_atomic_publishing(self):
        # unfortunately we've to mock here to avoid that the product is actually published to ebay
        schedule_ebay_item_publish_mock = \
            self.patch('inventorum.ebay.apps.products.resources.schedule_ebay_item_publish')

        # Note: This id must be identical to the id in the JSON fixture
        inv_product_id = 463690

        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
        category = CategoryFactory.create()
        product.category = category
        product.shipping_services.create(service=self.get_shipping_service_dhl(), cost=Decimal("20.00"))
        product.save()

        self.threaded_core_api_fake.whenGET("/api/products/%s" % inv_product_id,
                                            status=status.HTTP_200_OK,
                                            body=JSONFixture.load("core_api/product.json"))

        self.threaded_core_api_fake.whenGET("/api/info/",
                                            status=status.HTTP_200_OK,
                                            body=JSONFixture.load("core_api/account_info.json"))

        self.threaded_core_api_fake.whenPOST("/api/products/%s/state/" % inv_product_id,
                                             status=status.HTTP_200_OK)

        async_requests = [grequests.post(self.url_for(port, "/products/%s/publish" % inv_product_id),
                                         headers=self.credentials) for port in self.ports]
        responses = grequests.map(async_requests)

        self.assertEqual(len([r for r in responses if r.status_code == status.HTTP_200_OK]), 1)
        self.assertEqual(len([r for r in responses if r.status_code == status.HTTP_400_BAD_REQUEST]), 9)

        self.assertEqual(schedule_ebay_item_publish_mock.call_count, 1)
