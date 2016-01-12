# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal as D

from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.apps.orders import CorePaymentMethod
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.shipping import INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.ebay.data import BuyerPaymentMethodCodeType
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreAPIDataSerializers(UnitTestCase, ShippingServiceTestMixin):

    def test_complete_order(self):
        # assert regular, non-click-and-collect order ##################################################################

        shipping_service_dhl = self.get_shipping_service_dhl()

        order = OrderModelFactory.create(ebay_id="9912341245-123456789",
                                         buyer_first_name="Andreas",
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
                                         payment_amount=D("24.45"),

                                         ebay_status__is_paid=True,
                                         core_status__is_paid=True)

        OrderLineItemModelFactory.create(order=order,
                                         orderable_item__inv_product_id=23,
                                         name="Inventorum T-Shirt [Green, L]",
                                         unit_price=D("3.99"),
                                         tax_rate=D("7"),
                                         quantity=5)

        OrderLineItemModelFactory.create(order=order,
                                         orderable_item__inv_product_id=24,
                                         name="Inventorum Pants [Red, XXL]",
                                         unit_price=D("19.99"),
                                         tax_rate=D("7"),
                                         quantity=2)

        serializer = OrderModelCoreAPIDataSerializer(order)

        self.assertDictEqual(serializer.data, {
            "channel": "ebay",
            "basket": {
                "items": [
                    {
                        "product": 24,
                        "name": "Inventorum Pants [Red, XXL]",
                        "quantity": 2,
                        "unit_gross_price": "19.99",
                        "tax_rate": "7.000"
                    },
                    {
                        "product": 23,
                        "name": "Inventorum T-Shirt [Green, L]",
                        "quantity": 5,
                        "unit_gross_price": "3.99",
                        "tax_rate": "7.000"
                    },
                ],
                "note_external": "Ebay order id: 9912341245-123456789"
            },
            "shipment": {
                "name": "DHL Paket",
                "cost": "4.50",
                "external_key": "DE_DHLPaket",
                "tracking_number": None,
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
            }],
            "state": BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID
        })

        # assert click-and-collect order ###############################################################################

        order.selected_shipping.service = self.get_shipping_service_click_and_collect()

        # also assert payment with bank transfer and initial order state when order was not paid yet
        order.ebay_payment_method = BuyerPaymentMethodCodeType.MoneyXferAccepted
        order.payment_method = CorePaymentMethod.from_ebay_payment_method(BuyerPaymentMethodCodeType.MoneyXferAccepted)
        order.ebay_status.is_paid = False
        order.core_status.is_paid = False
        order.save()

        self.assertPrecondition(order.is_click_and_collect, True)
        self.assertIsNotNone(order.pickup_code)

        serializer = OrderModelCoreAPIDataSerializer(order)
        data = serializer.data

        self.assertDictEqual(data["shipment"], {
            "name": "Click & Collect",
            "cost": "4.50",
            "external_key": INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID,
            "tracking_number": order.pickup_code,
            "service": {
                "name": "Click & Collect",
                "time_min": None,
                "time_max": None
            }
        })

        self.assertEqual(data["payments"][0]["payment_method"], CorePaymentMethod.BANK_TRANSFER)
        self.assertEqual(data["state"], BinaryCoreOrderStates.PENDING)
