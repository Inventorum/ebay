# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.functional import cached_property
from inventorum_ebay.apps.categories.models import CategoryModel
from inventorum_ebay.apps.categories.tests.factories import CategoryFactory
from inventorum_ebay.apps.products.serializers import EbayProductSerializer
from inventorum_ebay.apps.products.tests.factories import EbayProductFactory
from inventorum_ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum_ebay.apps.shipping.tests.factories import ShippingServiceFactory
from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase
from rest_framework import status


log = logging.getLogger(__name__)


class TestProductUpdate(EbayAuthenticatedAPITestCase, ShippingServiceTestMixin):

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

    def test_category_updates(self):
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

        get_product = self.client.get("/products/{inv_id}".format(inv_id=self.product.inv_id))
        self.assertEqual(get_product.data, self.get_valid_data_for(self.product))

    def test_click_and_collect_saving(self):
        assert self.product.category is None

        # set is_click_and_collect
        data = self.get_valid_data_for(self.product)
        data["is_click_and_collect"] = True

        response = self.request_update(self.product, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_product = self.product.reload()
        self.assertEqual(updated_product.is_click_and_collect, True)

        # remove is_click_and_collect
        data = response.data
        data["is_click_and_collect"] = False

        response = self.request_update(self.product, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_product = self.product.reload()
        self.assertEqual(updated_product.is_click_and_collect, False)

        get_product = self.client.get("/products/{inv_id}".format(inv_id=self.product.inv_id))
        self.assertEqual(get_product.data, self.get_valid_data_for(self.product))

    def test_shipping_service_updates(self):
        assert self.product.shipping_services.count() == 0

        dhl = self.get_shipping_service_dhl()
        hermes = self.get_shipping_service_hermes()

        data = self.get_valid_data_for(self.product)
        data["shipping_services"] = [{"service": dhl.pk,
                                      "cost": "5.90",
                                      "additional_cost": "0.30"},
                                     {"service": hermes.pk,
                                      "cost": "3.49",
                                      "additional_cost": "0.00"}]

        response = self.request_update(self.product, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.shipping_services.count(), 2)

        configured_service_ids = self.product.shipping_services.values_list("service_id", flat=True)
        self.assertItemsEqual(configured_service_ids, [dhl.pk, hermes.pk])
