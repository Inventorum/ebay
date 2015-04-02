# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D

from django.conf import settings

from inventorum.ebay.tests.testcases import UnitTestCase

from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient, CoreAPIClient
from mock import patch


log = logging.getLogger(__name__)


class TestUserScopedCoreAPIClient(UnitTestCase):

    def setUp(self):
        super(TestUserScopedCoreAPIClient, self).setUp()

        self.user_id = 42
        self.account_id = 23

        self.subject = UserScopedCoreAPIClient(user_id=self.user_id, account_id=self.account_id)

    def test_default_headers(self):
        expected_version = settings.VERSION

        self.assertEqual(self.subject.default_headers, {
            "User-Agent": "inv-ebay/{version}".format(version=expected_version),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Inv-User": unicode(self.user_id),
            "X-Inv-Account": unicode(self.account_id)
        })

    def test_get_products_returns_core_product(self):
        # TODO jm: Make it a proper end-to-end test when api_internal in staging is reachable from vpn

        core_product_json = {
            "price": "419.3300000000",
            "gross_price": "448.68",
            "purchase_price": "399.0000000000",
            "average_price": "419.32977310924",
            "average_purchase_price": "399.0000000000",
            "is_favourite": False,
            "stock": 90,
            "reorder": 10,
            "safety": 5,
            "images": [],
            "tax_rate": 7,
            "address": "",
            "shipping_services": [],
            "categories": [
                {
                    "parent": None,
                    "is_leaf": True,
                    "hint": None,
                    "tree_id": 21841,
                    "id": 22022,
                    "channel": None,
                    "translations": [
                        {
                            "id": 344,
                            "language": "de",
                            "name": "Fixies"
                        }
                    ],
                    "image": None,
                    "products_count": 1,
                    "products": [
                        330857
                    ]
                }
            ],
            "shop_url": None,
            "ebay_url": None,
            "in_shop": False,
            "meta": {
                "ebay": {
                    "images": [],
                    "price": "419.3300000000",
                    "gross_price": "448.68",
                    "id": 520,
                    "channel": 4,
                    "name": "",
                    "description": ""
                }
            },
            "id": 330857,
            "name": "Felt Brougham",
            "description": "Marvellous bike",
            "supplier": "",
            "brand": "",
            "product_code": "10001",
            "gtin": "1234567890000",
            "ebay_product_id": None,
            "custom_price": False,
            "is_giftcard": False,
            "attributes": [],
            "tags": []
        }

        class FakeResponse(object):
            def __init__(self, json_fixture):
                self.json_fixture = json_fixture

            def json(self):
                return self.json_fixture

        with patch.object(CoreAPIClient, 'get', return_value=FakeResponse(core_product_json)) as patched_get:
            subject = UserScopedCoreAPIClient(user_id=23, account_id=42)

            core_product = subject.get_product(330857)
            patched_get.assert_called_with("/api/products/330857")

            self.assertEqual(core_product.id, 330857)
            self.assertEqual(core_product.name, "Felt Brougham")
            self.assertEqual(core_product.description, "Marvellous bike")
            self.assertEqual(core_product.gross_price, D("448.68"))
            self.assertEqual(core_product.stock, D("90"))

            # meta attr overwrites

            core_product_json["meta"]["ebay"].update({
                "name": "ebay name",
                "description": "ebay description",
                "gross_price": "999.99"
            })

            core_product = subject.get_product(330857)

            self.assertEqual(core_product.name, "ebay name")
            self.assertEqual(core_product.description, "ebay description")
            self.assertEqual(core_product.gross_price, D("999.99"))
