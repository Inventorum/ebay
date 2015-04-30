# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import json

from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer, EbayLocationSerializer
from inventorum.ebay.apps.accounts.tests.factories import EbayLocationFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from rest_framework import status


log = logging.getLogger(__name__)


class TestEbayAccountResource(EbayAuthenticatedAPITestCase):

    def request_get_account(self):
        return self.client.get("/account/")

    def request_put_account(self, data):
        return self.client.put("/account/", data=data)

    def get_serialized_data_for(self, account):
        return EbayAccountSerializer(account).data

    def test_serializers(self):
        get_response = self.request_get_account()
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data, self.get_serialized_data_for(self.account))

        put_response = self.request_put_account(get_response.data)
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.data, self.get_serialized_data_for(self.account))

    def test_location_get_put(self):
        EbayLocationFactory.create(account=self.account)

        get_response = self.request_get_account()
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data, self.get_serialized_data_for(self.account))

        put_response = self.request_put_account(get_response.data)
        log.debug('Got response: %s', put_response.data)
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.data, self.get_serialized_data_for(self.account))

    def test_location_save_new(self):

        get_response = self.request_get_account()
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data, self.get_serialized_data_for(self.account))
        data = get_response.data

        location = EbayLocationFactory.create()
        location_data = EbayLocationSerializer(instance=location).data
        data['location'] = location_data

        put_response = self.request_put_account(data)
        log.debug('Got response: %s', put_response.data)
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)

        account = self.account.reload()
        self.assertDictEqual(put_response.data, self.get_serialized_data_for(account))

        new_location = account.location
        self.assertNotEqual(location.id, new_location.id)

        new_location_data = EbayLocationSerializer(instance=new_location).data
        self.assertDictEqual(location_data, new_location_data)
