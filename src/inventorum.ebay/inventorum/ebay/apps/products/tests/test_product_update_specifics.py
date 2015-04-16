# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from rest_framework import status

from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory
from inventorum.ebay.apps.products.serializers import EbayProductSerializer
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestProductUpdateSpecifics(EbayAuthenticatedAPITestCase):

    def setUp(self):
        super(TestProductUpdateSpecifics, self).setUp()
        self.leaf_category = self._build_leaf_category_with_specifics()

    def _build_leaf_category_with_specifics(self):
        root_category = CategoryFactory.create(name="Root category")
        level_2_category = CategoryFactory.create(name="Level 2 category", parent=root_category)
        leaf_category = CategoryFactory.create(name="Leaf category", parent=level_2_category)

        specific = CategorySpecificFactory.create(category=leaf_category)
        required_specific = CategorySpecificFactory.create_required(category=leaf_category)

        required_specific_selection_only = CategorySpecificFactory.create_required(category=leaf_category,
                                                                                   selection_mode='SelectionOnly')
        self.assertFalse(required_specific_selection_only.can_use_own_values)

        self.assertEqual(leaf_category.specifics.count(), 3)
        return leaf_category

    def _get_valid_data_for(self, product):
        return EbayProductSerializer(product).data

    def _request_update(self, product, data):
        return self.client.put("/products/{inv_id}".format(inv_id=product.inv_id), data=data)

    def test_valid_saving(self):
        product = EbayProductFactory.create(category=self.leaf_category)
        data = self._get_valid_data_for(product)
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)



