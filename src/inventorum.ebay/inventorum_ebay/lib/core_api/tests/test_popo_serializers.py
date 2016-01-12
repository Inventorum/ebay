# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging

from inventorum_ebay.lib.core_api.models import CoreProductDeserializer, CoreProductDeltaDeserializer
from inventorum_ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreProductDeserializer(UnitTestCase):

    def test_meta_overwrite(self):
        minimal_core_product_json = {
            "ean": None,
            "gross_price": "448.68",
            "tax_type": 1001,
            "quantity": 90,
            "images": [{"id": 2915, "urls": {"ipad": "http://image/ipad", "ipad_retina": "http://image/ipad_retina"}}],
            "meta": {
                "ebay": {
                    "images": [],
                    "gross_price": None,
                    "id": 520,
                    "channel": 4,
                    "name": None,
                    "description": ""
                }
            },
            "id": 330857,
            "name": "Felt Brougham",
            "variation_count": 0,
            "shipping_services": [],
            "attributes": {},
            "description": "Marvellous bike"
        }

        subject = CoreProductDeserializer(data=minimal_core_product_json)
        subject.is_valid(raise_exception=True)

        core_product = subject.build()
        # None in meta should be ignored
        self.assertEqual(core_product.ean, None)
        self.assertEqual(core_product.name, "Felt Brougham")
        self.assertEqual(core_product.description, "Marvellous bike")
        self.assertEqual(len(core_product.images), 1)
        self.assertEqual(core_product.gross_price, Decimal("448.68"))
        self.assertEqual(core_product.images[0].id, 2915)
        self.assertFalse(core_product.is_parent)

        # Update meta
        minimal_core_product_json["meta"]["ebay"] = {
            "images": [{"id": 9999, "urls": {"ipad": "http://image/ipad", "ipad_retina": "http://image/ipad_retina"}}],
            "gross_price": "500.00",
            "id": 520,
            "channel": 4,
            "name": "Some ebay name",
            "description": "Some ebay description"
        }

        subject = CoreProductDeserializer(data=minimal_core_product_json)
        subject.is_valid(raise_exception=True)

        core_product = subject.build()
        self.assertEqual(core_product.name, "Some ebay name")
        self.assertEqual(core_product.description, "Some ebay description")
        self.assertEqual(core_product.gross_price, Decimal("500.00"))
        self.assertEqual(len(core_product.images), 1)
        self.assertEqual(core_product.images[0].id, 9999)


class TestCoreProductDeltaDeserializer(UnitTestCase):

    def test_meta_overwrite(self):
        minimal_core_delta_product_json = {
            "id": 1,
            "name": "Some product",
            "state": "updated",
            "gross_price": "449.99",
            "quantity": 1337,
            "meta": {
                "ebay": {
                    "gross_price": "449.99"
                }
            }
        }

        subject = CoreProductDeltaDeserializer(data=minimal_core_delta_product_json)
        subject.is_valid(raise_exception=True)

        core_delta_product = subject.build()
        self.assertEqual(core_delta_product.gross_price, Decimal("449.99"))

        # Update meta
        minimal_core_delta_product_json["meta"]["ebay"]["gross_price"] = "500.00"
        subject = CoreProductDeltaDeserializer(data=minimal_core_delta_product_json)
        subject.is_valid(raise_exception=True)

        core_delta_product = subject.build()
        self.assertEqual(core_delta_product.gross_price, Decimal("500.00"))
