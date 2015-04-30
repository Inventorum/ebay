# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal as D
import logging
from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.shipping.tests import ShippingServiceConfigurableSerializerTest, ShippingServiceTestMixin
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestEbayAccountSerializer(UnitTestCase, ShippingServiceConfigurableSerializerTest):

    # Required interface for ShippingServiceConfigurableSerializerTest

    def get_serializer_class(self):
        return EbayAccountSerializer

    def get_entity(self):
        return EbayAccountFactory.create()

    # / Required interface for ShippingServiceConfigurableSerializerTest

    def get_account_with_default_data(self):
        account = EbayAccountFactory.create()
        account.shipping_services.create(service=self.get_shipping_service_dhl(),
                                         cost=D("3.49"))
        return account

    def test_serialize(self):
        account = self.get_account_with_default_data()
        shipping_service = account.shipping_services.first()

        subject = EbayAccountSerializer(account)
        self.assertEqual(subject.data, {
            "shipping_services": [{
                "service": shipping_service.service_id,
                "external_id": "DE_DHLPaket",
                "cost": "3.49",
                "additional_cost": "0.00"
            }],
            'user_id': account.user_id,
            'email': account.email
        })

    def test_deserialize_serialized(self):
        account = self.get_account_with_default_data()

        serialized = EbayAccountSerializer(account).data

        subject = EbayAccountSerializer(account, data=serialized)
        subject.is_valid(raise_exception=True)
        subject.save()

        updated_account = account.reload()

        # deserialize serialized doesn't change the representation
        data_before = serialized
        self.assertEqual(EbayAccountSerializer(updated_account).data, data_before)
