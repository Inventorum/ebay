# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.utils.functional import cached_property

from inventorum.ebay.apps.categories.models import CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.core_api.tests import ApiTest
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.tasks import schedule_ebay_item_publish
from inventorum.ebay.tests import StagingTestAccount

from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from inventorum.util.celery import TaskExecutionContext, celery_test_case


log = logging.getLogger(__name__)


class TestProductPublish(EbayAuthenticatedAPITestCase):

    # @celery_test_case()
    def test_foo(self):
        for i in range(0, 8):
            schedule_ebay_item_publish(i, context=TaskExecutionContext(user_id=i, account_id=i, request_id=i))

    @cached_property
    def category(self):
        return CategoryFactory.create(external_id="176973")

    def _assign_category(self, product):
        product.category = self.category
        product.save()

        features = CategoryFeaturesModel.objects.create(
            category=self.category
        )
        durations = ['Days_5', 'Days_30']
        for d in durations:
            duration = DurationModel.objects.create(
                value=d
            )
            features.durations.add(duration)

    @ApiTest.use_cassette("publish_product_resource_no_category.yaml")
    def test_publish_no_category(self):
        inv_product_id = StagingTestAccount.Products.SIMPLE_PRODUCT_ID
        assert not EbayProductModel.objects.by_inv_id(inv_product_id).exists()

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertEqual(data, ['You need to select category'])


    @ApiTest.use_cassette("publish_product_that_does_not_exists.yaml")
    def test_publish_not_existing_one(self):
        inv_product_id = StagingTestAccount.Products.PRODUCT_NOT_EXISTING

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 404)

    @ApiTest.use_cassette("unpublish_product_that_does_not_exists.yaml")
    def test_unpublish_not_existing_one(self):
        inv_product_id = StagingTestAccount.Products.PRODUCT_NOT_EXISTING
        response = self.client.post("/products/%s/unpublish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 404)

    @ApiTest.use_cassette("publish_and_unpublish_full.yaml")
    def test_publish_then_unpublish(self):
        inv_product_id = StagingTestAccount.Products.IPAD_STAND
        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
        self._assign_category(product)

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/products/%s/unpublish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)
