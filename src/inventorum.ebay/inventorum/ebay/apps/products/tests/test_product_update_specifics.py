# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.functional import cached_property
from inventorum.ebay.apps.products.models import EbayProductSpecificModel, EbayProductModel

from rest_framework import status

from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory
from inventorum.ebay.apps.products.serializers import EbayProductSerializer
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestProductUpdateSpecifics(EbayAuthenticatedAPITestCase):
    def setUp(self):
        super(TestProductUpdateSpecifics, self).setUp()
        self.leaf_category = self._build_leaf_category_with_specifics()

    @cached_property
    def valid_category(self):
        parent = CategoryFactory.create(name="Parent category")
        return CategoryFactory.create(name="Valid category", parent=parent)

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
        data['specific_values'] = [
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
        data['specific_values'] = [
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
        Test save specifics to product. Sending here specifics without one required
        :return:
        """
        product = EbayProductFactory.create(category=self.leaf_category, account=self.account)
        selection_only_specific_value = self.required_specific_selection_only.values.last().value
        data = self._get_valid_data_for(product)
        data['specific_values'] = [
            {
                "specific": self.specific.pk,
                "value": "Some non-standard value"
            },
            # Missing here one of required specifics (we have 2 required ones)
            {
                "specific": self.required_specific_selection_only.pk,
                "value": selection_only_specific_value
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
        'non_field_errors': ['You need to pass all required specifics (missing: [%s])!' % self.required_specific.pk]})
        specific_values = product.specific_values.all()
        self.assertEqual(specific_values.count(), 0)

    def test_save_wrong_value(self):
        """
        Test save specifics to product. Sending here one that accepts
        only specific values, sending wrong non standard value.
        :return:
        """
        product = EbayProductFactory.create(category=self.leaf_category, account=self.account)
        selection_only_specific_value = self.required_specific_selection_only.values.last().value
        data = self._get_valid_data_for(product)
        data['specific_values'] = [
            {
                "specific": self.specific.pk,
                "value": "Some non-standard value"
            },
            {
                "specific": self.required_specific.pk,
                "value": "Some non-standard value"  # Should be accepted!
            },
            {
                "specific": self.required_specific_selection_only.pk,
                "value": "Wrong value!"
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'specific_values': [{}, {},
                {'non_field_errors': ['This item specific does not accept custom values (wrong: `Wrong value!`)']}
            ]})

        specific_values = product.specific_values.all()
        self.assertEqual(specific_values.count(), 0)

    def test_save_wrong_specific_category(self):
        """
        Test save specifics to product. Sending here specific id that belongs to other category.
        :return:
        """

        second_leaf_category = CategoryFactory.create(name="Leaf category 2")
        wrong_category_specific = CategorySpecificFactory.create(category=second_leaf_category)

        product = EbayProductFactory.create(category=self.leaf_category, account=self.account)
        selection_only_specific_value = self.required_specific_selection_only.values.last().value
        data = self._get_valid_data_for(product)
        data['specific_values'] = [
            {
                "specific": wrong_category_specific.pk,
                "value": "Some non-standard value"
            },
            {
                "specific": self.required_specific.pk,
                "value": "Some non-standard value"  # Should be accepted!
            },
            {
                "specific": self.required_specific_selection_only.pk,
                "value": selection_only_specific_value
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'non_field_errors': [
                'Some specifics are assigned to different category than product! (wrong specific ids: [%s])'
                % wrong_category_specific.pk
            ]
        })

        specific_values = product.specific_values.all()
        self.assertEqual(specific_values.count(), 0)

    def test_saving_with_category(self):
        """
        This test proves that when we save specific with category, it will be saved correctly!
        """
        selection_only_specific_value = self.required_specific_selection_only.values.last().value

        product = EbayProductFactory.create(account=self.account)
        data = self._get_valid_data_for(product)
        data['category'] = {
            'id': self.leaf_category.pk
        }
        data['specific_values'] = [
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

    def test_simple_deserializer_serialize(self):
        product = EbayProductFactory.create(account=self.account)
        data = self._get_valid_data_for(product)
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_more_than_one_value_in_one_specific_miss_one(self):
        """
        We said we have required 2 but we are sending only one, should fail!
        :return:
        """

        multiple_required = CategorySpecificFactory.create(category=self.leaf_category,
                                                           selection_mode='SelectionOnly',
                                                           min_values=2,
                                                           max_values=5)
        selection_only_specific_value = self.required_specific_selection_only.values.last().value

        product = EbayProductFactory.create(account=self.account)
        data = self._get_valid_data_for(product)
        data['category'] = {
            'id': self.leaf_category.pk
        }
        data['specific_values'] = [
            {
                "specific": multiple_required.pk,
                "value": multiple_required.values.all()[0].value
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'non_field_errors':
                ['You need to pass all required specifics (missing: [%s])!' % multiple_required.pk]
        })

    def test_more_than_one_value_in_one_specific_send_more_than_max(self):
        """
        self.required_specific has max_values as 1 but we are sending 2, so it should fail
        """

        selection_only_specific_value = self.required_specific_selection_only.values.last().value

        product = EbayProductFactory.create(account=self.account)
        data = self._get_valid_data_for(product)
        data['category'] = {
            'id': self.leaf_category.pk
        }
        data['specific_values'] = [
            {
                "specific": self.required_specific.pk,
                "value": "Some non-standard value"  # Should be accepted!
            },
            {
                "specific": self.required_specific.pk,
                "value": "Max was 1, so we are sending to much"  # Should fail!
            },
            {
                "specific": self.required_specific_selection_only.pk,
                "value": selection_only_specific_value  # Needs to be one of values
            }
        ]
        response = self._request_update(product, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'non_field_errors': ['You send too many values for one specific (specific_ids: [%s])!'
                                 % self.required_specific.pk]
        })


    def test_more_than_one_value_in_one_specific_valid(self):
        """
        We said we have required 2 but we are sending only one, should fail!
        :return:
        """

        multiple_required = CategorySpecificFactory.create(category=self.leaf_category,
                                                           selection_mode='SelectionOnly',
                                                           min_values=2,
                                                           max_values=5)
        selection_only_specific_value = self.required_specific_selection_only.values.last().value

        product = EbayProductFactory.create(account=self.account)
        data = self._get_valid_data_for(product)
        data['category'] = {
            'id': self.leaf_category.pk
        }
        data['specific_values'] = [
            {
                "specific": multiple_required.pk,
                "value": multiple_required.values.all()[0].value
            },
            {
                "specific": multiple_required.pk,
                "value": multiple_required.values.all()[1].value
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

        product = EbayProductModel.objects.get(id=product.id)
        values = product.specific_values_for_current_category.filter(specific_id=multiple_required.id)
        self.assertEqual(values.count(), 2)
        self.assertEqual(product.specific_values_for_current_category.count(), 4)