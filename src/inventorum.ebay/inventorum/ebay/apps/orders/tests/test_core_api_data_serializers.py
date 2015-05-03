# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.ebay.data import BuyerPaymentMethodCodeType

from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreAPIDataSerializers(UnitTestCase, ShippingServiceTestMixin):

    def test_without_payment_and_shipping(self):
        shipping_service_dhl = self.get_shipping_service_dhl()

        order = OrderModelFactory.create(buyer_first_name="Andreas",
                                         buyer_last_name="Balke",
                                         buyer_email="andi@inventorum.com",

                                         shipping_first_name="Christoph",
                                         shipping_last_name="Brem",
                                         shipping_address1="Voltastraße 5",
                                         shipping_address2="Inventorum, Gebäude 10",
                                         shipping_postal_code="13355",
                                         shipping_city="Berlin",
                                         shipping_state="Wedding",
                                         shipping_country="DE",

                                         selected_shipping__service=shipping_service_dhl,
                                         selected_shipping__cost=D("4.50"),

                                         payment_method=BuyerPaymentMethodCodeType.PayPal,
                                         payment_amount=D("24.45"))

        OrderLineItemModelFactory.create(order=order,
                                         orderable_item__product__inv_id=23,
                                         name="Inventorum T-Shirt [Green, L]",
                                         unit_price=D("3.99"),
                                         quantity=5)

        serializer = OrderModelCoreAPIDataSerializer(order)

        # TODO jm: Sync with core api
        self.assertDictEqual(serializer.data, {
            "items": [{"product": 23, "name": "Inventorum T-Shirt [Green, L]", "quantity": 5, "gross_price": "3.99"}],
            "shipment": {
                "name": "DHL Paket",
                "cost": "4.50",
                "external_id": "DE_DHLPaket"
            },
            "customer": {
                "first_name": "Andreas",
                "last_name": "Balke",
                "email": "andi@inventorum.com",
                "shipping_address": [{
                    "first_name": "Christoph",
                    "last_name": "Brem",
                    "address1": "Voltastraße 5",
                    "address2": "Inventorum, Gebäude 10",
                    "zipcode": "13355",
                    "city": "Berlin",
                    "state": "Wedding",
                    "country": "DE"
                }],
                "billing_address": {  # equals shipping address
                    "first_name": "Christoph",
                    "last_name": "Brem",
                    "address1": "Voltastraße 5",
                    "address2": "Inventorum, Gebäude 10",
                    "zipcode": "13355",
                    "city": "Berlin",
                    "state": "Wedding",
                    "country": "DE"
                }
            },
            "payments": [{
                "payment_method": BuyerPaymentMethodCodeType.PayPal,
                "payment_amount": "24.45"
            }]
        })
