# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.models import CoreProductDeserializer
from inventorum.ebay.apps.core_api.tests import CoreApiTest

from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreProductDeserializer(UnitTestCase):

    def test_null_meta_attributes_should_fallback_to_parent(self):
        minimal_core_product_json = {
            "gross_price": "448.68",
            "quantity": 90,
            "images": [{"id": 2915, "ipad": "http://image/ipad", "ipad_retina": "http://image/ipad_retina"}],
            "meta": {
                "ebay": {
                    "images": [],
                    "gross_price": "448.68",
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
        self.assertTrue(subject.is_valid(raise_exception=True))

        core_product = subject.build()
        # None in meta should be ignored
        self.assertEqual(core_product.name, "Felt Brougham")
        self.assertEqual(core_product.description, "Marvellous bike")
        self.assertEqual(len(core_product.images), 1)
        self.assertEqual(core_product.images[0].id, 2915)
        self.assertFalse(core_product.is_parent)