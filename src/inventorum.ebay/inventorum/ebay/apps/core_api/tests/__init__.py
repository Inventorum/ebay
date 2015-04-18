# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
from decimal import Decimal as D

from django.conf import settings
from inventorum.ebay.apps.accounts.models import EbayUserModel
from inventorum.ebay.tests import StagingTestAccount
import vcr


log = logging.getLogger(__name__)


CoreApiTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'core_api'),
    record_mode='once'
)

ApiTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'core_api'),
    record_mode='once'
)

MockedTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'mocked'),
    record_mode='once'
)


EbayTest = vcr.VCR(
    serializer='yaml',
    cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'ebay'),
    record_mode='once',
    filter_headers=['X-EBAY-API-APP-NAME', 'X-EBAY-API-CERT-NAME', 'X-EBAY-API-DEV-NAME', 'Authorization']
)


class CoreApiTestHelpers(object):
    """
    TestCase mixin that provides utility methods for core-api related tests

    Should be used in test cases that inherit from `APITestCase` as it expects an authenticated user/account

    *Caution*: These helpers will hit he actual core api, so use them wisely :-)
    """

    def create_core_api_product(self, name, gross_price="100.00", quantity=100, description=""):
        user = self.__authenticated_test_user

        tax_rate = D("19")
        net_price = (D(gross_price) / (tax_rate/D(100) + D(1)))

        TEN_PLACES = D(10) ** -10
        net_price = net_price.quantize(TEN_PLACES)

        response = user.core_api.post("/api/products/", data={
            "name": name,
            "description": description,
            "price": str(net_price),
            "tax_type": StagingTestAccount.TAX_TYPE_19_ID,
            "quantity": quantity,
            "reorder_level": 10,
            "safety_stock": 5,
            "images": []
        })

        json_body = response.json()
        log.debug("Core API product created: {}".format(json_body))
        return json_body["id"]

    def update_core_api_product(self, id, attributes):
        user = self.__authenticated_test_user
        return user.core_api.put("/api/products/{product_id}/".format(product_id=id), attributes)

    def delete_core_api_product(self, id):
        user = self.__authenticated_test_user
        return user.core_api.delete("/api/products/{product_id}/".format(product_id=id))

    @property
    def __authenticated_test_user(self):
        """ :rtype: EbayUserModel """
        assert isinstance(self.user, EbayUserModel)
        return self.user
