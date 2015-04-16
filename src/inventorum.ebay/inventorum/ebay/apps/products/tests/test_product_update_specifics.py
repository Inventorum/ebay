# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.products.models import EbayProductSpecificModel

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

        self.specific = CategorySpecificFactory.create(category=leaf_category)
        self.required_specific = CategorySpecificFactory.create_required(category=leaf_category)

        self.required_specific_selection_only = CategorySpecificFactory.create_required(category=leaf_category,
                                                                                        selection_mode='SelectionOnly')
        self.assertFalse(self.required_specific_selection_only.can_use_own_values)

        self.assertEqual(leaf_category.specifics.count(), 3)
        return leaf_category

    def _get_valid_data_for(self, product):
        return EbayProductSerializer(product).data

    def _request_update(self, product, data):
        return self.client.put("/products/{inv_id}".format(inv_id=product.inv_id), data=data)

    def test_valid_saving(self):
        """
        Test save specifics to product. Sending all valid values.
        """
        selection_only_specific_value = self.required_specific_selection_only.values.last().value

        product = EbayProductFactory.create(category=self.leaf_category, account=self.account)
        data = self._get_valid_data_for(product)
        data['specifics_values'] = [
            {
                "specific": self.specific.pk,
                "value": "Some non-standard value - not required"  # Should be accepted!
            },
            {
                "specific": self.required_specific.pk,
                "value": "Some non-standard value"  # Should be accepted!
            },
            {
                "specific": self.required_specific_selection_only.pk,
                "value": selection_only_specific_value  # Needs to be one of values
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        specific_values = product.specific_values.all()
        self.assertEqual(specific_values.count(), 3)

        self.assertEqual(specific_values.get(specific=self.specific).value, "Some non-standard value - not required")
        self.assertEqual(specific_values.get(specific=self.required_specific).value, "Some non-standard value")
        self.assertEqual(specific_values.get(specific=self.required_specific_selection_only).value,
                         selection_only_specific_value)

        # So everything is fine, lets remove non-required one!
        data = response.data
        data['specifics_values'] = [
            {
                "specific": self.required_specific.pk,
                "value": "Some non-standard value"  # Should be accepted!
            },
            {
                "specific": self.required_specific_selection_only.pk,
                "value": selection_only_specific_value  # Needs to be one of values
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        specific_values = product.specific_values.all()
        self.assertEqual(specific_values.count(), 2)

        with self.assertRaises(EbayProductSpecificModel.DoesNotExist):
            specific_values.get(specific=self.specific)

        self.assertEqual(specific_values.get(specific=self.required_specific).value, "Some non-standard value")
        self.assertEqual(specific_values.get(specific=self.required_specific_selection_only).value,
                         selection_only_specific_value)


    def test_save_validation_handling(self):
        """
        Test save specifics to product. Sending here specifics without one required and with one that accepts
        only specific values, sending wrong non standard value
        :return:
        """
        product = EbayProductFactory.create(category=self.leaf_category, account=self.account)
        data = self._get_valid_data_for(product)
        data['specifics_values'] = [
            {
                "specific": self.specific.pk,
                "value": "Some non-standard value"  # Should be accepted!
            },
            # Missing here one of required specifics (we have 2 required ones)
            {
                "specific": self.required_specific_selection_only.pk,
                "value": "Some not standard value, should fail!"
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        specific_values = product.specific_values.all()
        self.assertEqual(specific_values.count(), 0)