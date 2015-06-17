# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from decimal import Decimal
from django.conf import settings
import grequests
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.models import EbayProductModel

from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.tests.live_server_test import ConcurrentLiveServerTestCase, ThreadedCoreAPIFake
from inventorum.ebay.tests.utils import JSONFixture, PatchMixin


log = logging.getLogger(__name__)


class TestAtomicPublishingActions(ConcurrentLiveServerTestCase, ProductTestMixin, PatchMixin, ShippingServiceTestMixin):

    @classmethod
    def setUpClass(cls):
        host, port = settings.INV_CORE_API_HOST.split(":")
        cls.threaded_core_api_fake = ThreadedCoreAPIFake(host=host, port=int(port))
        cls.threaded_core_api_fake.daemon = True
        cls.threaded_core_api_fake.start()
        super(TestAtomicPublishingActions, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.threaded_core_api_fake.stop()
        cls.threaded_core_api_fake.join()

        super(TestAtomicPublishingActions, cls).tearDownClass()

    def test_it(self):
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
                                            respond_with=JSONFixture.load("core_api/product.json"))

        self.threaded_core_api_fake.whenGET("/api/info/",
                                            respond_with=JSONFixture.load("core_api/account_info.json"))

        async_requests = [grequests.post(self.url_for(port, "/products/%s/publish" % inv_product_id),
                                         headers=self.credentials) for port in self.ports]
        responses = grequests.map(async_requests)

        log.info([r.content for r in responses])

        self.assertEqual(schedule_ebay_item_publish_mock.call_count, 1)
