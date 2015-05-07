# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from inventorum.ebay.apps.orders import CorePaymentMethod
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.shipping import INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin

from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreAPIDataSerializers(UnitTestCase, ShippingServiceTestMixin):

    def test_complete_order(self):
        # assert regular, non-click-and-collect order ##################################################################

        shipping_service_dhl = self.get_shipping_service_dhl()

        order = OrderModelFactory.create(buyer_first_name="Andreas",
                                         buyer_last_name="Balke",
                                         buyer_email="andi@inventorum.com",

                                         shipping_address__name="Christoph Brem",
                                         shipping_address__street="Voltastraße 5",
                                         shipping_address__street1="Inventorum, Gebäude 10",
                                         shipping_address__postal_code="13355",
                                         shipping_address__city="Berlin",
                                         shipping_address__region="Wedding",
                                         shipping_address__country="DE",

                                         billing_address__name="Andreas Balke",
                                         billing_address__street="Voltastraße 5",
                                         billing_address__street1="Inventorum, Gebäude 10",
                                         billing_address__postal_code="13355",
                                         billing_address__city="Berlin",
                                         billing_address__region="Wedding",
                                         billing_address__country="DE",

                                         selected_shipping__service=shipping_service_dhl,
                                         selected_shipping__cost=D("4.50"),

                                         payment_method=CorePaymentMethod.PAYPAL,
                                         payment_amount=D("24.45"))

        OrderLineItemModelFactory.create(order=order,
                                         orderable_item__product__inv_id=23,
                                         name="Inventorum T-Shirt [Green, L]",
                                         unit_price=D("3.99"),
                                         tax_rate=D("7"),
                                         quantity=5)

        serializer = OrderModelCoreAPIDataSerializer(order)

        self.assertDictEqual(serializer.data, {
            "channel": "ebay",
            "basket": {
                "items": [{
                    "product": 23,
                    "name": "Inventorum T-Shirt [Green, L]",
                    "quantity": 5,
                    "unit_gross_price": "3.99",
                    "tax_rate": "7.000"
                }]
            },
            "shipment": {
                "name": "DHL Paket",
                "cost": "4.50",
                "external_id": "DE_DHLPaket",
                "service": {
                    "name": "DHL Paket",
                    "time_min": 60 * 60 * 24 * 1,
                    "time_max": 60 * 60 * 24 * 3
                }
            },
            "customer": {
                "first_name": "Andreas",
                "last_name": "Balke",
                "email": "andi@inventorum.com",
                "billing_address": {
                    "first_name": "Andreas",
                    "last_name": "Balke",
                    "address1": "Voltastraße 5",
                    "address2": "Inventorum, Gebäude 10",
                    "zipcode": "13355",
                    "city": "Berlin",
                    "state": "Wedding",
                    "country": "DE"
                },
                "shipping_address": [{
                    "first_name": "Christoph",
                    "last_name": "Brem",
                    "address1": "Voltastraße 5",
                    "address2": "Inventorum, Gebäude 10",
                    "zipcode": "13355",
                    "city": "Berlin",
                    "state": "Wedding",
                    "country": "DE"
                }]
            },
            "payments": [{
                "payment_amount": "24.45",
                "payment_method": CorePaymentMethod.PAYPAL
            }]
        })

        # assert click-and-collect order ###############################################################################

        order.selected_shipping.service = self.get_shipping_service_click_and_collect()
        self.assertPrecondition(order.is_click_and_collect, True)

        serializer = OrderModelCoreAPIDataSerializer(order)
        data = serializer.data

        self.assertDictEqual(data["shipment"], {
            "name": "Click & Collect",
            "cost": "4.50",
            "external_id": INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID,
            "service": {
                "name": "Click & Collect",
                "time_min": None,
                "time_max": None
            }
        })
