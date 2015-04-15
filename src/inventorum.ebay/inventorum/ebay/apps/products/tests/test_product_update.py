# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.functional import cached_property
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.serializers import EbayProductSerializer
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from rest_framework import status


log = logging.getLogger(__name__)


class TestProductUpdate(EbayAuthenticatedAPITestCase):

    def request_update(self, product, data):
        return self.client.put("/products/{inv_id}".format(inv_id=product.inv_id), data=data)

    @cached_property
    def product(self):
        return EbayProductFactory.create(account=self.account)

    @cached_property
    def valid_category(self):
        parent = CategoryFactory.create(name="Parent category")
        return CategoryFactory.create(name="Valid category", parent=parent)

    def get_valid_data_for(self, product):
        return EbayProductSerializer(product).data

    def test_serializer(self):
        data = self.get_valid_data_for(self.product)
        response = self.request_update(self.product, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = EbayProductSerializer(self.product).data
        self.assertEqual(response.data, expected_data)

    def test_category_assignment_and_removal(self):
        assert self.product.category is None

        # assign category
        data = self.get_valid_data_for(self.product)
        data["category"] = {
            "id": self.valid_category.id
        }

        response = self.request_update(self.product, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_product = self.product.reload()
        self.assertEqual(updated_product.category_id, self.valid_category.id)

        # remove category
        data = response.data
        data["category"] = None

        response = self.request_update(self.product, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_product = self.product.reload()
        self.assertEqual(updated_product.category_id, None)
