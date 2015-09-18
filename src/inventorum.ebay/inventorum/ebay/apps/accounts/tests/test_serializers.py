# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import json

from decimal import Decimal as D
from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer, AddressSerializer
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayLocationFactory, AddressFactory
from inventorum.ebay.apps.returns import ReturnsAcceptedOption, ReturnsWithinOption, ShippingCostPaidByOption
from inventorum.ebay.apps.returns.models import ReturnPolicyModel

from inventorum.ebay.apps.shipping.tests import ShippingServiceConfigurableSerializerTest
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
        location = EbayLocationFactory.create(account=account)
        account.return_policy = ReturnPolicyModel.objects.create(
            returns_accepted_option=ReturnsAcceptedOption.ReturnsAccepted,
            returns_within_option=ReturnsWithinOption.Days_14,
            shipping_cost_paid_by_option=ShippingCostPaidByOption.Buyer,
            description='The article can be returned in the given time frame')
        account.save()

        subject = EbayAccountSerializer(account)
        # Crazy trick to have nice diff in case of failure

        self.assertDictEqual(subject.data, {
            "shipping_services": [{
                                      "service": shipping_service.service_id,
                                      "external_id": "DE_DHLPaket",
                                      "cost": "3.49",
                                      "additional_cost": "0.00"
                                  }],
            'user_id': account.user_id,
            'email': account.email,
            'payment_method_bank_transfer_enabled': False,
            'payment_method_paypal_enabled': True,
            'payment_method_paypal_email_address': 'bartosz@hernas.pl',
            'location': {
                'name': location.name,
                'url': location.url,
                'longitude': unicode(location.longitude),
                'phone': location.phone,
                'address': {
                    'name': location.address.name,
                    'street': location.address.street,
                    'street1': location.address.street1,
                    'city': location.address.city,
                    'region': location.address.region,
                    'country': unicode(location.address.country),
                    'postal_code': location.address.postal_code,
                },
                'latitude': unicode(location.latitude),
                'pickup_instruction': location.pickup_instruction
            },
            'return_policy': {
                'returns_accepted_option': 'ReturnsAccepted',
                'returns_within_option': 'Days_14',
                'shipping_cost_paid_by_option': 'Buyer',
                'description': 'The article can be returned in the given time frame'
            }
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

    def test_serialize_address(self):
        address = AddressFactory.create(country=None)
        subject = AddressSerializer(address)

        # I am doing it to get
        # TypeError: Country(code=None) is not JSON serializable
        # As we got Server Error with it
        data = json.loads(json.dumps(subject.data))
        self.assertDictEqual(data, {
            'name': address.name,
            'street': address.street,
            'street1': address.street1,
            'city': address.city,
            'region': address.region,
            'country': unicode(address.country),
            'postal_code': address.postal_code,
        })

    def test_return_policy_create_and_update(self):
        self.assertFalse(self.account.has_return_policy, 'Precondition: Account should not have return policy')

        serializer = EbayAccountSerializer(self.account, partial=True, data={
            'return_policy': {
                'returns_accepted_option': ReturnsAcceptedOption.ReturnsAccepted,
                'returns_within_option': ReturnsWithinOption.Months_1,
                'shipping_cost_paid_by_option': ShippingCostPaidByOption.Seller,
                'description': 'Awesome descriptions are awesome'
            }})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_account = self.account.reload()
        self.assertTrue(updated_account.has_return_policy, 'Postcondition: Return policy should have been created')
        self.assertEqual(updated_account.return_policy.returns_accepted_option, ReturnsAcceptedOption.ReturnsAccepted)
        self.assertEqual(updated_account.return_policy.returns_within_option, ReturnsWithinOption.Months_1)
        self.assertEqual(updated_account.return_policy.shipping_cost_paid_by_option, ShippingCostPaidByOption.Seller)
        self.assertEqual(updated_account.return_policy.description, 'Awesome descriptions are awesome')

        return_policy_id = updated_account.return_policy.id

        # update the return policy
        serializer = EbayAccountSerializer(self.account, partial=True, data={
            'return_policy': {
                'returns_accepted_option': ReturnsAcceptedOption.ReturnsNotAccepted,
                'returns_within_option': None,
                'shipping_cost_paid_by_option': None,
                'description': None
            }})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_account = self.account.reload()
        self.assertEqual(updated_account.return_policy.id, return_policy_id, 'The serializer should update an existing '
                                                                             'policy and not create a new one')
        self.assertEqual(updated_account.return_policy.returns_accepted_option, ReturnsAcceptedOption.ReturnsNotAccepted)
        self.assertEqual(updated_account.return_policy.returns_within_option, None)
        self.assertEqual(updated_account.return_policy.shipping_cost_paid_by_option, None)
        self.assertEqual(updated_account.return_policy.description, None)
