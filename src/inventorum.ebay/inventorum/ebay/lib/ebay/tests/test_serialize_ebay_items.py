from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal
from contextlib import contextmanager
from inventorum.ebay.lib.ebay.data.items import EbayGetItemResponse, EbayFixedPriceItem

from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.accounts.tests import AccountTestMixin
from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.lib.ebay.tests.example_ebay_item_response import EbayResponseItemExample
from inventorum.ebay.lib.celery import celery_test_case
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


@contextmanager
def published_product(self, with_variations=False):
    """Publish a product and ensure that the product is unpublished when the context exits."""
    assert all(isinstance(self, c) for c in (EbayAuthenticatedAPITestCase, ProductTestMixin, AccountTestMixin))
    self.prepare_account_for_publishing(self.account)

    items = EbayItems(self.ebay_token)
    response = items.get_all_items_from_seller_list()

    if with_variations:
        product = self.get_valid_ebay_product_with_variations_for_publishing(self.account)
    else:
        product = self.get_valid_ebay_product_for_publishing(account=self.account)
    response = self.client.post('/products/%s/publish' % product.inv_id)
    log.debug('Got response: %s', response)
    self.assertEqual(response.status_code, 200)

    item = product.items.first()
    self.assertEqual(
        item.publishing_status,
        EbayItemPublishingStatus.PUBLISHED,
        'Check if the @celery_test_case is missing or if the product is already published on ebay.'
    )
    self.assertTrue(item)
    try:
        yield product, item
    finally:
        self.client.post('/products/%s/unpublish' % product.inv_id)


class TestGetDataFromEbay(EbayAuthenticatedAPITestCase, ProductTestMixin, AccountTestMixin):

    @celery_test_case()
    @EbayTest.use_cassette("full_test_for_serialize_get_item_ids_from_ebay.yaml")
    def test_published_item_is_found_when_reading_published_items_on_ebay(self):
        with published_product(self) as (products, item):
            items = EbayItems(self.ebay_token)
            response = items.get_all_items_from_seller_list()
            self.assertTrue(any(i.item_id == item.external_id for i in response.items))

    @celery_test_case()
    @EbayTest.use_cassette("full_test_for_serialize_get_item_from_ebay.yaml")
    def test_reading_items_with_variations(self):
        with published_product(self, with_variations=True) as (product, item):
            ebay_client = EbayItems(self.ebay_token)
            item1 = ebay_client.get_item(item.external_id)
            self.assertEqual(item1.item_id, item.external_id)
            self.assertEqual(item1.start_price.value, Decimal('130.00'))
            self.assertEqual(item1.title, 'Jeans Valid Attrs')
            self.assertEqual(item1.sku, 'invtest_666032')
            self.assertEqual(item1.country, 'DE')
            self.assertEqual(item1.postal_code, '13355')
            self.assertEqual(item1.shipping_details.shipping_service_options[0].shipping_service, 'DE_DHLPaket')
            self.assertEqual(item1.primary_category.category_id, '57989')
            self.assertEqual(item1.listing_duration, 'Days_30')
            self.assertEqual(item1.payment_methods, 'PayPal')
            self.assertEqual(item1.paypal_email_address, 'info@inventorum.com')
            self.assertTrue(item1.pictures[0].url.endswith('JPEG'))
            self.assertIsNone(item1.ean)
            self.assertEqual(item.variations.all().count(), 2)

    @celery_test_case()
    @EbayTest.use_cassette("serialize_get_not_expired_items_from_ebay.yaml")
    def test_not_get_expired_items_from_ebay(self):
        with published_product(self) as (product, item):
            items = EbayItems(self.ebay_token)
            response = items.get_all_items_from_seller_list(entries_per_page=1)

            self.assertTrue(response.items)

            for item in response.items:
                current_item = items.get_item(item.item_id)
                self.assertEqual(item.item_id, current_item.item_id)

    def test_serialize_data_from_ebay(self):
        ebay_response_example = EbayResponseItemExample.response
        item = EbayGetItemResponse.create_from_data(data=ebay_response_example)
        self.assertIsInstance(item, EbayFixedPriceItem)
