# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import unittest
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.core_api.tests import CoreApiTest
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.tests import StagingTestAccount

from inventorum.ebay.tests.testcases import APITestCase, EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestProductPublish(EbayAuthenticatedAPITestCase):
    def _assign_category(self, product):
        category, c = CategoryModel.objects.get_or_create(external_id='176973')
        product.category = category
        product.save()

        features = CategoryFeaturesModel.objects.create(
            category=category
        )
        durations = ['Days_5', 'Days_30']
        for d in durations:
            duration = DurationModel.objects.create(
                value=d
            )
            features.durations.add(duration)

    @CoreApiTest.vcr.use_cassette("publish_product_resource_no_category.json")
    def test_publish_no_category(self):
        inv_product_id = StagingTestAccount.Products.SIMPLE_PRODUCT_ID
        assert not EbayProductModel.objects.by_inv_id(inv_product_id).exists()

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertEqual(data, ['You need to select category'])


    @CoreApiTest.vcr.use_cassette("publish_product_resource_valid_one.json")
    def test_publish_valid_one(self):
        inv_product_id = StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING

        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=self.account)
        self._assign_category(product)

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertEqual(data, [
            u'Die eingegebene E-Mail-Adresse ist nicht mit einem PayPal-Konto verknüpft. Sollten Sie noch kein '
            u'PayPal-Konto haben, richten Sie mit dieser Adresse bitte eines ein, damit Ihre Käufer Sie bezahlen '
            u'können. (Sie können Ihr Konto auch einrichten, nachdem der Artikel verkauft wurde.)',
            u'Der Artikel kann weder eingestellt noch bearbeitet werden. Die Artikelbezeichnung und/oder -beschreibung '
            u'enthalten unter Umständen unzulässige Begriffe oder das Angebot verstößt gegen die '
            u'eBay-Grundsätze.']
        )

