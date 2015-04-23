# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import json

from django.utils.functional import cached_property

from inventorum.ebay.apps.categories.models import CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory
from inventorum.ebay.apps.core_api import PublishStates
from inventorum.ebay.apps.core_api.tests import ApiTest
from inventorum.ebay.apps.products import EbayItemPublishingStatus, EbayApiAttemptType
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.services import PublishingPreparationService
from inventorum.ebay.apps.products.tests.factories import EbayProductSpecificFactory
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.lib.celery import celery_test_case

from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestProductPublish(EbayAuthenticatedAPITestCase):
    @cached_property
    def category(self):
        return CategoryFactory.create(external_id="176973")

    def _assign_category(self, product, category=None, durations=None):
        category = category or self.category
        product.category = category
        product.save()

        features = CategoryFeaturesModel.objects.create(
            category=category
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

    @celery_test_case()
    @ApiTest.use_cassette("publish_and_unpublish_full.yaml")
    def test_publish_then_unpublish(self):
        inv_product_id = StagingTestAccount.Products.IPAD_STAND
        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
        self._assign_category(product)

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.assertEqual(item.attempts.count(), 1)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.PUBLISH)

        response = self.client.post("/products/%s/unpublish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)

        # Publish & Unpublish = 2
        self.assertEqual(item.attempts.count(), 2)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.UNPUBLISH)

    @celery_test_case()
    def test_failing_publish(self):
        with ApiTest.use_cassette("failing_publish.yaml") as cass:
            inv_product_id = StagingTestAccount.Products.IPAD_STAND
            product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
            self._assign_category(product, durations=['Days_120'])  # Send wrong duration

            response = self.client.post("/products/%s/publish" % inv_product_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            item = product.items.last()
            self.assertEqual(item.publishing_status, EbayItemPublishingStatus.FAILED)

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

            self.assertEqual(headers['X-EBAY-API-DEV-NAME'], "dbedb016-ee04-4fce-a8e3-22c134fbb3c7")
            self.assertEqual(headers['X-EBAY-API-CERT-NAME'], "6be1b82a-0372-4e15-822d-e93797d623ac")
            self.assertEqual(headers['X-EBAY-API-APP-NAME'], "Inventor-9021-41d8-9c25-9bae93f76429")
            self.assertEqual(headers['X-EBAY-API-SITEID'], 77)

            self.assertEqual(last_attempt.request.method, 'POST')
            self.assertEqual(last_attempt.request.url, 'https://api.ebay.com/ws/api.dll')

            self.assertIn("<RequesterCredentials>", last_attempt.request.body)
            self.assertNotIn("<eBayAuthToken>", last_attempt.request.body)

            self.assertEqual(last_attempt.response.status_code, 200)
            self.assertTrue(last_attempt.response.headers)

            self.assertEqual(last_attempt.response.url, 'https://api.ebay.com/ws/api.dll')
            self.assertIn('AddFixedPriceItemResponse', last_attempt.response.content)

    @celery_test_case()
    def test_failing_unpublish(self):
        with ApiTest.use_cassette("failing_unpublishing.yaml") as cass:
            inv_product_id = StagingTestAccount.Products.IPAD_STAND
            product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
            self._assign_category(product)

            service = PublishingPreparationService(product, self.user)
            item = service.create_ebay_item()
            item.external_id = '1234'
            item.publishing_status = EbayItemPublishingStatus.PUBLISHED
            item.save()

            response = self.client.post("/products/%s/unpublish" % inv_product_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            self.assertEqual(item.attempts.count(), 1)
            last_attempt = item.attempts.last()
            self.assertFalse(last_attempt.success)
            self.assertEqual(last_attempt.type, EbayApiAttemptType.UNPUBLISH)

            requests = cass.requests
            status_change_requests = [r for r in requests if r.url.endswith('/state/')]
            self.assertEqual(len(status_change_requests), 2)

            state_body = json.loads(status_change_requests[1].body)
            self.assertEqual(state_body['state'], PublishStates.PUBLISHED)
            self.assertEqual(state_body['details'], [
                {
                    'classification': 'RequestError',
                    'code': 17,
                    'long_message': 'Der Artikel kann nicht aufgerufen werden, da er gel\xf6scht wurde, es sich um ein '
                                    'Half.com-Angebot handelt oder weil Sie nicht der Verk\xe4ufer sind.',
                    'severity_code': 'Error',
                    'short_message': 'Artikel kann nicht aufgerufen werden.'
                }])


    @celery_test_case()
    def test_publish_then_unpublish_variation_unsupported_category(self):
        with ApiTest.use_cassette("publish_and_unpublish_full_variation_unsupported_cat.yaml") as cass:
            inv_product_id = StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS
            product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
            self._assign_category(product)

            response = self.client.post("/products/%s/publish" % inv_product_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            item = product.items.last()
            self.assertEqual(item.publishing_status, EbayItemPublishingStatus.FAILED)
            last_request = cass.requests[5]
            body = json.loads(last_request.body)
            self.assertEqual(body, {
                'channel': 'ebay',
                'details': [
                    {
                        'classification': 'RequestError',
                        'code': 21916564,
                        'long_message': 'Die ausgew\xe4hlte Kategorie unterst\xfctzt keine Angebote mit Varianten',
                        'severity_code': 'Error',
                        'short_message': 'In dieser Kategorie werden keine Varianten unterst\xfctzt'
                    }, {
                        'classification': 'RequestError',
                        'code': 21916672,
                        'long_message': 'Das bzw. die Tags material sind als Variante deaktiviert.',
                        'severity_code': 'Error',
                        'short_message': 'Als Variantenfehler deaktiviert.'
                    }],
                'state': 'failed'
            })


    @celery_test_case()
    def test_publish_then_unpublish_variation_supported_category_missing_specifics(self):
        with ApiTest.use_cassette("publish_and_unpublish_full_variation_missing_specifics.yaml") as cass:
            inv_product_id = StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS
            product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
            category = CategoryFactory.create(external_id="53159")
            CategorySpecificFactory.create(category=category)
            required_specific = CategorySpecificFactory.create_required(category=category)

            self._assign_category(product, category=category)

            response = self.client.post("/products/%s/publish" % inv_product_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data, [
                'You need to pass all required specifics (missing: [%s])!' % required_specific.pk
            ])

    @celery_test_case()
    def test_publish_then_unpublish_variation_supported_category(self):
        with ApiTest.use_cassette("publish_and_unpublish_full_variation.yaml") as cass:
            inv_product_id = StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS
            product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
            category = CategoryFactory.create(external_id="53159")
            size_specific = CategorySpecificFactory.create_required(category=category, name="Größe")
            brand_specific = CategorySpecificFactory.create_required(category=category, name="Marke")
            self._assign_category(product, category=category)

            EbayProductSpecificFactory.create(
                product=product,
                specific=size_specific,
                value="22"
            )

            EbayProductSpecificFactory.create(
                product=product,
                specific=brand_specific,
                value="Adidas"
            )

            response = self.client.post("/products/%s/publish" % inv_product_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.assertEqual(item.attempts.count(), 1)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.PUBLISH)

        response = self.client.post("/products/%s/unpublish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)

        # Publish & Unpublish = 2
        self.assertEqual(item.attempts.count(), 2)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.UNPUBLISH)
