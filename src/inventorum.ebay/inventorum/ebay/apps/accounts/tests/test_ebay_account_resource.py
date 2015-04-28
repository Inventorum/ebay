# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.accounts.serializers import EbayAccountSerializer
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
