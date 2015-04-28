# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D, Decimal

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
            "X-Api-Version": 9,
            "X-Inv-User": unicode(self.user_id),
            "X-Inv-Account": unicode(self.account_id)
        })

    @CoreApiTest.use_cassette("get_product_simple.yaml")
    def test_get_products_without_ebay_meta(self):
        core_product = self.subject.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID)

        self.assertEqual(core_product.id, StagingTestAccount.Products.SIMPLE_PRODUCT_ID)
        self.assertEqual(core_product.name, "XtC Advanced 2 LTD")
        self.assertEqual(core_product.description, "GIANT XtC 27.5\" Advanced Carbon")
        self.assertEqual(core_product.gross_price, D("1999.99"))
        self.assertEqual(core_product.quantity, D("1000"))

        self.assertEqual(len(core_product.images), 1)
        image = core_product.images[0]
        self.assertEqual(image.id, 2914)
        self.assertTrue(image.url.endswith(
            "/uploads/img-hash/f6ac/f910/410a/1ce2/9f24/6d92/ea14/f6acf910410a1ce29f246d92ea1402ae_ipad_retina.JPEG"))


    @CoreApiTest.use_cassette("get_product_with_ebay_meta.yaml")
    def test_get_product_with_ebay_meta(self):
        core_product = self.subject.get_product(StagingTestAccount.Products.PRODUCT_WITH_EBAY_META_ID)

        self.assertEqual(core_product.id, StagingTestAccount.Products.PRODUCT_WITH_EBAY_META_ID)
        # non-channeled name: FastRoad CoMax
        self.assertEqual(core_product.name, "eBay: FastRoad CoMax")
        # non-channeled description: GIANT FastRoad CoMax Carbon
        self.assertEqual(core_product.description, "eBay: GIANT FastRoad CoMax Carbon")
        # non-channeled gross price: 1999.99
        self.assertEqual(core_product.gross_price, D("1599.99"))
        self.assertEqual(core_product.quantity, D("1000"))

        # non-channeled product has only one image
        self.assertEqual(len(core_product.images), 2)

        image_1 = core_product.images[0]
        self.assertEqual(image_1.id, 2915)
        self.assertTrue(image_1.url.endswith(
            "/uploads/img-hash/565b/9fd7/fb15/0563/2747/a01d/b8f8/565b9fd7fb1505632747a01db8f823c6_ipad_retina.JPEG"))

        image_2 = core_product.images[1]
        self.assertEqual(image_2.id, 2916)
        self.assertTrue(image_2.url.endswith(
            "/uploads/img-hash/ede0/531d/fdd7/b267/d6bc/1662/d548/ede0531dfdd7b267d6bc1662d5483562_ipad_retina.JPEG"))

    @CoreApiTest.use_cassette("get_product_with_shipping_services.yaml")
    def test_get_product_with_ebay_meta(self):
        core_product = self.subject.get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES)

        self.assertEqual(core_product.id, StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES)
        self.assertEqual(len(core_product.shipping_services), 2)

        first_shipping = core_product.shipping_services[0]
        self.assertEqual(first_shipping.id, 'DE_HermesPaket')
        self.assertEqual(first_shipping.description, 'Hermes Paket')
        self.assertEqual(first_shipping.time_min, 1)
        self.assertEqual(first_shipping.time_max, 2)
        self.assertEqual(first_shipping.additional_cost, Decimal(1))
        self.assertEqual(first_shipping.cost, Decimal(10))

    @CoreApiTest.use_cassette("get_account_info.yaml")
    def test_get_account_info(self):
        core_account = self.subject.get_account_info()
        self.assertEqual(core_account.account.email, "tech+slingshot-test@inventorum.com")
        self.assertEqual(core_account.account.country, "DE")

        billing = core_account.account.billing_address
        self.assertEqual(billing.address1, "Voltastr 5")
        self.assertEqual(billing.address2, "Gebaude 3")
        self.assertEqual(billing.zipcode, "13355")
        self.assertEqual(billing.city, "Berlin")
        self.assertEqual(billing.state, None)
        self.assertEqual(billing.country, "DE")
        self.assertEqual(billing.first_name, "John")
        self.assertEqual(billing.last_name, "Newman")
        self.assertEqual(billing.company, "Inventorum")

        account_settings = core_account.account.settings
        self.assertEqual(len(account_settings.shipping_services), 1)
        self.assertEqual(account_settings.ebay_paypal_email, 'bartosz@hernas.pl')
        self.assertEqual(account_settings.ebay_payment_methods, ['PayPal'])
        self.assertTrue(account_settings.ebay_click_and_collect)

        shipping_service = account_settings.shipping_services[0]
        self.assertEqual(shipping_service.id, 'DE_DHLPaket')
        self.assertEqual(shipping_service.description, 'DHL Paket')
        self.assertEqual(shipping_service.additional_cost, Decimal('2'))
        self.assertEqual(shipping_service.cost, Decimal('5'))

    @CoreApiTest.use_cassette("get_product_with_variations.yaml")
    def test_product_with_variations(self):
        product = self.subject.get_product(StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS)

        self.assertEqual(product.name, "Jeans Valid Attrs")
        self.assertEqual(product.description, "Photo of jeans for sell.")
        self.assertEqual(product.gross_price, D("0.00"))
        self.assertEqual(product.quantity, D("80"))

        self.assertEqual(product.variation_count, 2)
        self.assertEqual(len(product.variations), 2)

        first_variation = product.variations[0]
        self.assertEqual(first_variation.name, "Red, 22")
        self.assertEqual(first_variation.gross_price, D("150"))
        self.assertEqual(first_variation.quantity, D("30"))

        self.assertEqual(len(first_variation.attributes), 3)
        self.assertEqual(first_variation.attributes[0].key, "color")
        self.assertEqual(first_variation.attributes[0].values, ['Red'])

        self.assertEqual(first_variation.attributes[1].key, "material")
        self.assertEqual(first_variation.attributes[1].values, ['Denim'])

        self.assertEqual(first_variation.attributes[2].key, "size")
        self.assertEqual(first_variation.attributes[2].values, ['22'])

        self.assertEqual(len(first_variation.images), 1)
        self.assertTrue(first_variation.images[0].url.startswith("https://app.inventorum.net/uploads/"))

        second_variation = product.variations[1]
        self.assertEqual(second_variation.name, "Blue, 50")
        self.assertEqual(second_variation.gross_price, D("130"))
        self.assertEqual(second_variation.quantity, D("50"))

        self.assertEqual(len(second_variation.attributes), 3)
        self.assertEqual(second_variation.attributes[0].key, "color")
        self.assertEqual(second_variation.attributes[0].values, ['Blue'])

        self.assertEqual(second_variation.attributes[1].key, "material")
        self.assertEqual(second_variation.attributes[1].values, ['Leather'])

        self.assertEqual(second_variation.attributes[2].key, "size")
        self.assertEqual(second_variation.attributes[2].values, ['50'])

        self.assertEqual(len(second_variation.images), 1)
        self.assertTrue(second_variation.images[0].url.startswith("https://app.inventorum.net/uploads/"))
