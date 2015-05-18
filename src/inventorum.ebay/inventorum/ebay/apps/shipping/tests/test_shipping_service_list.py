# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.shipping.serializers import ShippingServiceSerializer
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.apps.shipping.tests.factories import ShippingServiceFactory
from inventorum.ebay.tests import Countries
from rest_framework import status
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestShippingServiceList(EbayAuthenticatedAPITestCase, ShippingServiceTestMixin):

    def setUp(self):
        super(TestShippingServiceList, self).setUp()

        # Invariant: default country of shipping services must equal default account country
        assert self.account.country == ShippingServiceFactory.country

    def test_list(self):
        # name = UPS Express
        ups = self.get_shipping_service_ups()
        # name = DHL Paket
        dhl = self.get_shipping_service_dhl()
        # name = Hermes Paket
        hermes = self.get_shipping_service_hermes()

        response = self.get_shipping_services()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_shipping_services_in_response(response, [dhl, hermes, ups])

    def test_filters_by_country(self):
        dhl_de = ShippingServiceFactory.create(external_id="DE_DHL_Express")
        dhl_at = ShippingServiceFactory.create(external_id="AT_DHL_Express", country=Countries.AT)

        response = self.get_shipping_services()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_shipping_services_in_response(response, [dhl_de])

        self.account.country = Countries.AT
        self.account.save()

        response = self.get_shipping_services()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_shipping_services_in_response(response, [dhl_at])

    def get_shipping_services(self):
        return self.client.get("/shipping/services")

    def assert_shipping_services_in_response(self, response, expected_shipping_services):
        """
        Asserts that the expected shipping services (in the given order) are in the given response
        :param response: The actual response
        :param expected_shipping_services: The expected shipping services (order is irrelevant)
        :type expected_shipping_services: list[inventorum.ebay.apps.shipping.models.ShippingServiceModel]
        """
        expected_shipping_service_data = ShippingServiceSerializer(expected_shipping_services, many=True).data
        actual_shipping_service_data = response.data
        self.assertEqual(actual_shipping_service_data, expected_shipping_service_data)
