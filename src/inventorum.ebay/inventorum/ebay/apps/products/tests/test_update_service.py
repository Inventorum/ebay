# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal as D
import logging

from inventorum.ebay.tests import MockedTest
from inventorum.ebay.apps.products import EbayItemUpdateStatus
from inventorum.ebay.apps.products.services import UpdateService, UpdateFailedException
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, PublishedEbayItemFactory, \
    EbayItemUpdateFactory, EbayItemVariationUpdateFactory, EbayItemVariationFactory, EbayItemVariationSpecificFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from ebaysdk.response import Response as EbayResponse, ResponseDataObject


log = logging.getLogger(__name__)


class IntegrationTestUpdateService(EbayAuthenticatedAPITestCase):
    def setUp(self):
        super(IntegrationTestUpdateService, self).setUp()

        self.product = EbayProductFactory.create()
        self.published_item = PublishedEbayItemFactory(product=self.product,
                                                       account=self.account,
                                                       gross_price=D("1.99"),
                                                       quantity=10)

    def test_update_succeeded(self):
        # Note: The recorded cassette has been manually modified to return a successful response
        with MockedTest.use_cassette("test_update_service_success.yaml") as cassette:
            item_update = EbayItemUpdateFactory.create(item=self.published_item,
                                                       gross_price=D("4.20"),
                                                       quantity=23)

            subject = UpdateService(item_update, user=self.user)
            subject.update()

            item_update = item_update.reload()
            self.assertEqual(item_update.status, EbayItemUpdateStatus.SUCCEEDED)

            self.assertEqual(item_update.attempts.count(), 1)
            attempt = item_update.attempts.first()

            self.assertEqual(attempt.item.id, self.published_item.id)
            self.assertEqual(attempt.success, True)

            self.assertIn("<ReviseFixedPriceItemRequest", attempt.request.body)
            self.assertIn("<ItemID>1002</ItemID>", attempt.request.body)
            self.assertIn("<StartPrice>4.20</StartPrice>", attempt.request.body)
            self.assertIn("<Quantity>23</Quantity>", attempt.request.body)

            # ebay item model should have been updated
            self.published_item = self.published_item.reload()
            self.assertEqual(self.published_item.gross_price, D("4.20"))
            self.assertEqual(self.published_item.quantity, 23)

    def test_update_failed(self):
        # Note: The recorded cassette fails because the ebay account was blocked
        with MockedTest.use_cassette("test_update_service_failure.yaml"):
            item_update = EbayItemUpdateFactory.create(item=self.published_item,
                                                       gross_price=D("2.50"),
                                                       quantity=12)

            subject = UpdateService(item_update, user=self.user)
            with self.assertRaises(UpdateFailedException):
                subject.update()

            item_update = item_update.reload()

            self.assertEqual(item_update.attempts.count(), 1)
            attempt = item_update.attempts.first()

            self.assertEqual(attempt.item.id, self.published_item.id)
            self.assertEqual(attempt.success, False)

            self.assertEqual(item_update.status, EbayItemUpdateStatus.FAILED)
            self.assertEqual(item_update.status_details, [
                {
                    "long_message": "Das eBay-Konto f\u00fcr den in dieser Anfrage angegebenen Nutzernamen \"dejoh_dnju7\" wurde aufgehoben. Sie k\u00f6nnen leider nur Informationen f\u00fcr aktuelle Nutzer anfordern.",
                    "code": 841,
                    "severity_code": "Error",
                    "classification": "RequestError",
                    "short_message": "Das eBay-Konto des angeforderten Nutzers wurde aufgehoben.",
                    "parameters": ["dejoh_dnju7"]}])

            # ebay item model should *not* have been updated
            self.published_item = self.published_item.reload()
            self.assertEqual(self.published_item.gross_price, D("1.99"))
            self.assertEqual(self.published_item.quantity, 10)

    def test_update_succeeded_with_variations(self):
        # Note: The recorded cassette has been manually modified to return a successful response
        with MockedTest.use_cassette("test_update_service_success_with_variations.yaml") as cassette:
            item_update = EbayItemUpdateFactory.create(item=self.published_item,
                                                       gross_price=None,
                                                       quantity=None)
            variation_obj = EbayItemVariationFactory.create(
                item=self.published_item,
                gross_price=D("4.45"),
                quantity=1
            )

            EbayItemVariationSpecificFactory.create(
                variation=variation_obj,
                name='Specific 1'
            )

            EbayItemVariationSpecificFactory.create(
                variation=variation_obj,
                name='Specific 2'
            )

            second_variation_obj = EbayItemVariationFactory.create(
                item=self.published_item
            )

            EbayItemVariationSpecificFactory.create(
                variation=second_variation_obj,
                name='Specific 1'
            )

            EbayItemVariationSpecificFactory.create(
                variation=second_variation_obj,
                name='Specific 2'
            )

            EbayItemVariationUpdateFactory.create(
                update_item=item_update,
                variation=variation_obj,
                gross_price=D("123.45"),
                quantity=22
            )

            EbayItemVariationUpdateFactory.create(
                update_item=item_update,
                variation=second_variation_obj,
                is_deleted=True
            )

            subject = UpdateService(item_update, user=self.user)
            subject.update()

            item_update = item_update.reload()
            self.assertEqual(item_update.status, EbayItemUpdateStatus.SUCCEEDED)

            self.assertEqual(item_update.attempts.count(), 1)
            attempt = item_update.attempts.first()

            self.assertEqual(attempt.item.id, self.published_item.id)
            self.assertEqual(attempt.success, True)

            request = EbayResponse(ResponseDataObject({'content': attempt.request.body.encode('utf-8')}, []))
            data = request.dict()
            variation = data['ReviseFixedPriceItemRequest']['Item']['Variations']['Variation']

            self.assertEqual(len(variation), 2)

            first_variation = variation[0]
            self.assertEqual(first_variation, {
                'Quantity': '0',
                'StartPrice': '1.99',
                'SKU': 'invdev_{0}'.format(second_variation_obj.inv_product_id),
                'VariationSpecifics': {
                    'NameValueList': [
                        {
                            'Name': 'Specific 2 (*)',
                            'Value': ['Value 1', 'Value 2']
                        },
                        {
                            'Name': 'Specific 1 (*)',
                            'Value': ['Value 1', 'Value 2']
                        }
                    ]}
            })

            second_variation = variation[1]
            self.assertEqual(second_variation, {
                'Quantity': '22',
                'StartPrice': '123.45',
                'SKU': 'invdev_{0}'.format(variation_obj.inv_product_id),
                'VariationSpecifics': {
                    'NameValueList': [
                        {
                            'Name': 'Specific 2 (*)',
                            'Value': ['Value 1', 'Value 2']
                        },
                        {
                            'Name': 'Specific 1 (*)',
                            'Value': ['Value 1', 'Value 2']
                        }
                    ]}
            })

            # ebay item model should have been updated
            self.published_item = self.published_item.reload()
            self.assertEqual(self.published_item.gross_price, D("1.99"))
            self.assertEqual(self.published_item.quantity, 10)

            variation_obj_first = self.published_item.variations.first()
            self.assertEqual(variation_obj_first.gross_price, D("123.45"))
            self.assertEqual(variation_obj_first.quantity, 22)

            variation_obj_last = self.published_item.variations.last()
            self.assertEqual(variation_obj_last.quantity, 0)
