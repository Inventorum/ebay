# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import json

from django.utils.functional import cached_property

from inventorum.ebay.apps.categories.models import CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.core_api import PublishStates
from inventorum.ebay.apps.core_api.tests import CoreApiTest, ApiTest
from inventorum.ebay.apps.products import EbayProductPublishingStatus, EbayApiAttemptType
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

        self.assertEqual(item.attempts.count(), 1)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.PUBLISH)

        response = self.client.post("/products/%s/unpublish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayProductPublishingStatus.UNPUBLISHED)

        # Publish & Unpublish = 2
        self.assertEqual(item.attempts.count(), 2)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.UNPUBLISH)

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

            self.assertEqual(item.attempts.count(), 1)
            last_attempt = item.attempts.last()
            self.assertFalse(last_attempt.success)
            self.assertEqual(last_attempt.type, EbayApiAttemptType.PUBLISH)

            headers = last_attempt.request.headers
            headers.pop('X-EBAY-SDK-REQUEST-ID')
            self.assertEqual(headers, {
                "X-EBAY-API-SITEID": 77,
                "X-EBAY-API-DEV-NAME": "dbedb016-ee04-4fce-a8e3-22c134fbb3c7",
                "X-EBAY-API-CERT-NAME": "6be1b82a-0372-4e15-822d-e93797d623ac",
                "Content-Length": "2925",
                "X-EBAY-API-APP-NAME": "Inventor-9021-41d8-9c25-9bae93f76429",
                "X-EBAY-API-COMPATIBILITY-LEVEL": 911,
                "X-EBAY-API-CALL-NAME": "AddItem",
                "User-Agent": "eBaySDK/2.1.0-dev1 Python/2.7.8 Darwin/14.1.0",
                "Content-Type": "text/xml"})
            self.assertEqual(last_attempt.request.method, 'POST')
            self.assertEqual(last_attempt.request.url, 'https://api.ebay.com/ws/api.dll')

            self.assertIn("<RequesterCredentials>", last_attempt.request.body)
            self.assertNotIn("<eBayAuthToken>", last_attempt.request.body)

            self.assertEqual(last_attempt.response.status_code, 200)
            self.assertEqual(last_attempt.response.headers, {
                "x-ebay-request-id": "14cd670a-4170-a626-1634-21b4e6572b63!ws.api.dll!10.98.97.99!esbtrading[]",
                "content-length": "717",
                "x-ebay-esb-app-name": "Inventor-9021-41d8-9c25-9bae93f76429",
                "x-ebay-api-pool-name": "___cDRidW8ydmtv",
                "x-ebay-esb-call-name": "AddItem",
                "server": "Apache-Coyote/1.1",
                "x-ebay-api-server-name": "___ZW9nNGQ3MWYrNzY9ZSgyNSg+Oys3MjQrNzQyPz43OzU=",
                "date": "Mon, 20 Apr 2015 10:47:28 GMT",
                "x-ebay-esb-guid": "urn:uuid:ac65da94-45c2-4bf3-80c2-02f7938cf164",
                "guid": "14cd670a-4170-a626-1634-21b4e6572b63",
                "content-type": "text/xml",
                "x-ebay-esb-siteid": "77"})

            self.assertEqual(last_attempt.response.url, 'https://api.ebay.com/ws/api.dll')
            self.assertIn('AddItemResponse', last_attempt.response.content)


