# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import json
from decimal import Decimal as D

from ebaysdk.response import Response, ResponseDataObject
from inventorum.ebay.apps.accounts.tests import AccountTestMixin
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.lib.core_api import PublishStates
from inventorum.ebay.tests import IntegrationTest
from inventorum.ebay.apps.products import EbayItemPublishingStatus, EbayApiAttemptType
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.services import PublishingPreparationService
from inventorum.ebay.lib.celery import celery_test_case
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class IntegrationTestPublishingAndUnpublishing(EbayAuthenticatedAPITestCase, ProductTestMixin, AccountTestMixin):

    def setUp(self):
        super(IntegrationTestPublishingAndUnpublishing, self).setUp()
        self.prepare_account_for_publishing(self.account)

    @celery_test_case()
    @IntegrationTest.use_cassette('publishing/test_publishing_and_unpublishing.yaml')
    def test_publishing_and_unpublishing(self):
        product = self.get_valid_ebay_product_for_publishing(account=self.account)

        response = self.client.post('/products/%s/publish' % product.inv_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.assertEqual(item.attempts.count(), 1)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.PUBLISH)

        response = self.client.post('/products/%s/unpublish' % product.inv_id)
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
    def test_publishing_and_unpublishing_with_click_and_collect(self):
        product = self.get_valid_ebay_product_for_publishing(account=self.account)
        product.is_click_and_collect = True
        product.save()

        # remove all shipping services since they are not required for click & collect
        product.shipping_services.delete()
        self.account.shipping_services.delete()

        with IntegrationTest \
                .use_cassette('publishing/test_publishing_and_unpublishing_with_click_and_collect.yaml') as cass:
            response = self.client.post('/products/%s/publish' % product.inv_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            item = product.items.last()
            self.assertIsNotNone(item)
            self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)
            self.assertIsNotNone(item.published_at)
            self.assertIsNotNone(item.ends_at)
            self.assertIsNone(item.unpublished_at)

            response = self.client.post('/products/%s/unpublish' % product.inv_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            item = product.published_item
            self.assertIsNone(item)

            last_item = product.items.last()
            self.assertEqual(last_item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)
            self.assertIsNotNone(last_item.published_at)
            self.assertIsNotNone(last_item.unpublished_at)

        requests = cass.requests
        uris = [r.uri for r in requests]
        self.assertIn('https://api.ebay.com/selling/inventory/v1/inventory/delta/add', uris)
        self.assertIn('https://api.ebay.com/selling/inventory/v1/inventory/delta/delete', uris)

        inventory_add_request = None
        for r in requests:
            if r.uri == 'https://api.ebay.com/selling/inventory/v1/inventory/delta/add':
                inventory_add_request = r
                break

        self.assertIsNotNone(inventory_add_request)
        body = Response(ResponseDataObject({'content': inventory_add_request.body.encode('utf-8')}, [])).dict()
        self.assertEqual(body, {
            'AddInventoryRequest': {'Locations': {'Location': {'Availability': 'IN_STOCK',
                                                               'LocationID': 'invdev_346'}},
                                    'SKU': last_item.sku}})


    @celery_test_case()
    @IntegrationTest.use_cassette('publishing/test_publishing_and_unpublishing_with_variations.yaml')
    def test_publishing_and_unpublishing_with_variations(self):
        product = self.get_valid_ebay_product_with_variations_for_publishing(self.account)

        response = self.client.post('/products/%s/publish' % product.inv_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.assertEqual(item.attempts.count(), 1)
        last_attempt = item.attempts.last()
        self.assertTrue(last_attempt.success)
        self.assertEqual(last_attempt.type, EbayApiAttemptType.PUBLISH)

        response = self.client.post('/products/%s/unpublish' % product.inv_id)
        log.debug('Got response: %s', response.data)
        self.assertEqual(response.status_code, 200)

        # Trick api to think product was published
        item = product.items.last()
        item.publishing_status = EbayItemPublishingStatus.PUBLISHED
        item.save()

        # Try to unpublish already unpublished product
        response = self.client.post('/products/%s/unpublish' % product.inv_id)
        log.debug('Got response: %s', response.data)
        self.assertEqual(response.status_code, 200)

        item = product.items.last()
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)

        # Publish & Unpublish & Unpublish = 3
        self.assertEqual(item.attempts.count(), 3)
        first_unpublish_attempt = item.attempts.order_by('time_added', 'id')[1]
        self.assertTrue(first_unpublish_attempt.success)
        self.assertEqual(first_unpublish_attempt.type, EbayApiAttemptType.UNPUBLISH)

        # Last attempt should be successful cause we got that this item was already unpublished
        second_unpublish_attempt = item.attempts.order_by('time_added', 'id')[2]
        self.assertTrue(second_unpublish_attempt.success)
        self.assertEqual(second_unpublish_attempt.type, EbayApiAttemptType.UNPUBLISH)

    @celery_test_case()
    def test_publishing_attempt_with_ebay_error(self):
        # try to publish a product with variations to a category that does not support variations
        with IntegrationTest.use_cassette('publishing/test_publishing_attempt_with_ebay_error.yaml') as cass:
            inv_id = StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS
            product = self.get_valid_ebay_product_for_publishing(account=self.account, inv_id=inv_id)

            response = self.client.post('/products/%s/publish' % product.inv_id)
            log.debug('Got response: %s', response)
            self.assertEqual(response.status_code, 200)

            item = product.items.last()
            self.assertEqual(item.publishing_status, EbayItemPublishingStatus.FAILED)
            last_request = cass.requests[4]
            body = json.loads(last_request.body)
            self.assertEqual(body, {
                'channel': 'ebay',
                'details': [{'classification': 'RequestError',
                             'code': 21916564,
                             'long_message': 'Die ausgew\xe4hlte Kategorie unterst\xfctzt keine Angebote mit Varianten',
                             'parameters': [],
                             'severity_code': 'Error',
                             'short_message': 'In dieser Kategorie werden keine Varianten unterst\xfctzt'}],
                'state': 'failed'
            })

    @celery_test_case()
    def test_unpublishing_attempt_with_ebay_error(self):
        # try to unpublish an item with an invalid item id
        with IntegrationTest.use_cassette(
                'publishing/test_unpublishing_attempt_with_ebay_error.yaml') as cass:
            product = self.get_valid_ebay_product_for_publishing(self.account)

            service = PublishingPreparationService(product, self.user)
            item = service.create_ebay_item()
            item.external_id = '1234'
            item.publishing_status = EbayItemPublishingStatus.PUBLISHED
            item.save()

            response = self.client.post('/products/%s/unpublish' % product.inv_id)
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
                    'parameters': ['1234'],
                    'severity_code': 'Error',
                    'short_message': 'Artikel kann nicht aufgerufen werden.'
                }])

    @IntegrationTest.use_cassette('publishing/test_publishing_attempt_with_validation_error.yaml')
    def test_publishing_attempt_with_validation_error(self):
        inv_product_id = StagingTestAccount.Products.SIMPLE_PRODUCT_ID
        assert not EbayProductModel.objects.by_inv_id(inv_product_id).exists()

        self.account.shipping_services.create(service=self.get_shipping_service_dhl(),
                                              cost=D('5.00'), additional_cost=D('0.00'))

        response = self.client.post('/products/%s/publish' % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertEqual(data, ['You need to select category'])

    @IntegrationTest.use_cassette('publishing/test_publishing_attempt_for_non_existing_product.yaml')
    def test_publishing_attempt_for_non_existing_product(self):
        inv_product_id = StagingTestAccount.Products.PRODUCT_NOT_EXISTING

        response = self.client.post('/products/%s/publish' % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 404)

    def test_unpublishing_attempt_for_non_existing_product(self):
        inv_product_id = StagingTestAccount.Products.PRODUCT_NOT_EXISTING
        response = self.client.post('/products/%s/unpublish' % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 404)
