# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin

from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCoreAPIDataSerializers(UnitTestCase, ShippingServiceTestMixin):

    def test_without_payment_and_shipping(self):
        selected_shipping = ShippingServiceConfigurationModel.objects.create(service=self.get_shipping_service_dhl(),
                                                                             cost=D("4.50"))

        order = OrderModelFactory.create(selected_shipping=selected_shipping)

        published_ebay_item = PublishedEbayItemFactory(product__inv_id=23)
        OrderLineItemModelFactory.create(order=order,
                                         orderable_item=published_ebay_item,
                                         name="Inventorum T-Shirt [Green, L]",
                                         quantity=5, unit_price=D("3.99"))

        serializer = OrderModelCoreAPIDataSerializer(order)

        # TODO jm: Add rest of the data and sync with andi
        self.assertDictEqual(serializer.data, {
            "items": [{"product": 23, "name": "Inventorum T-Shirt [Green, L]", "quantity": 5, "gross_price": "3.99"}],
            "shipment": {
                "name": "DHL Paket",
                "cost": "4.50",
                "external_id": "DE_DHLPaket"
            }
        })
