# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import json

from django.utils.functional import cached_property

from inventorum.ebay.apps.categories.models import CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.core_api import PublishStates
from inventorum.ebay.apps.core_api.tests import CoreApiTest, ApiTest
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.tests import StagingTestAccount

from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestProductPublish(EbayAuthenticatedAPITestCase):
    @cached_property
    def category(self):
        return CategoryFactory.create(external_id="176973")

    def _assign_category(self, product, durations=None):
        product.category = self.category
        product.save()

        features = CategoryFeaturesModel.objects.create(
            category=self.category
        )
        durations = durations or ['Days_5', 'Days_30']
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

    @ApiTest.use_cassette("publish_and_unpublish_full.yaml", record_mode="new_episodes")
    def test_publish_then_unpublish(self):
        inv_product_id = StagingTestAccount.Products.IPAD_STAND
        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
        self._assign_category(product)

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayProductPublishingStatus.PUBLISHED)

        response = self.client.post("/products/%s/unpublish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayProductPublishingStatus.UNPUBLISHED)

    def test_failing_publish(self):
        with ApiTest.use_cassette("failing_publish.yaml") as cass:
            inv_product_id = StagingTestAccount.Products.IPAD_STAND
            product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
            self._assign_category(product, durations=['Days_120'])  # Send wrong duration

            response = self.client.post("/products/%s/publish" % inv_product_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            item = product.items.last()
            self.assertEqual(item.publishing_status, EbayProductPublishingStatus.FAILED)

            requests = cass.requests
            status_change_requests = [r for r in requests if r.url.endswith('/state/')]
            self.assertEqual(len(status_change_requests), 2)

            state_body = json.loads(status_change_requests[0].body)
            self.assertEqual(state_body['state'], PublishStates.IN_PROGRESS)

            state_body = json.loads(status_change_requests[1].body)
            self.assertEqual(state_body['state'], PublishStates.FAILED)
            self.assertEqual(state_body['details'], [
                {
                    'classification': 'RequestError',
                    'code': 83,
                    'long_message': 'Die Dauer "120" (in Tagen) ist f\xfcr dieses Angebotsformat nicht verf\xfcgbar, '
                                    'bzw. ung\xfcltig f\xfcr die Kategorie "176973".',
                    'severity_code': 'Error',
                    'short_message': 'Ung\xfcltige Dauer.'
                }])

