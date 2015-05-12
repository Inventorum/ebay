# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import date

import logging
import os
from decimal import Decimal as D

from django.conf import settings
from inventorum.ebay.apps.accounts.models import EbayUserModel
from inventorum.ebay.tests import StagingTestAccount
import vcr


log = logging.getLogger(__name__)


class CoreApiTestHelpers(object):
    """
    TestCase mixin that provides utility methods for core-api related tests

    Should be used in test cases that inherit from `APITestCase` as it expects an authenticated user/account

    *Caution*: These helpers will hit he actual core api, so use them wisely :-)
    """

    def create_core_api_product(self, name, gross_price="100.00", quantity=100, description=""):
        user = self.__authenticated_test_user

        net_price = gross_to_net(gross_price, tax_rate=D("19"))
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
        if "gross_price" in attributes:
            net_price = gross_to_net(D(attributes["gross_price"]), tax_rate=D("19"))
            attributes["price"] = str(net_price)

        user = self.__authenticated_test_user
        return user.core_api.put("/api/products/{product_id}/".format(product_id=id), attributes)

    def adjust_core_inventory(self, product_id, quantity, price=None, cost=None):
        user = self.__authenticated_test_user

        data = {
            "stock": {
                "quantity": quantity,
                "date": date.today().strftime("%d.%m.%Y"),
                "note": ""
            }
        }

        if price is None and cost is None:
            raise Exception("Either price or cost must be set")

        if price is not None:
            data["stock"]["price"] = price

        if cost is not None:
            data["stock"]["cost"] = cost

        return user.core_api.put("/api/products/{product_id}/adjust_inventory/".format(product_id=product_id),
                                 data=data)

    def delete_core_api_product(self, id):
        user = self.__authenticated_test_user
        return user.core_api.delete("/api/products/{product_id}/".format(product_id=id))

    @property
    def __authenticated_test_user(self):
        """ :rtype: EbayUserModel """
        assert isinstance(self.user, EbayUserModel)
        return self.user


def gross_to_net(price, tax_rate):
    TEN_PLACES = D(10) ** -10
    return (D(price) / (tax_rate/D(100) + D(1))).quantize(TEN_PLACES)
