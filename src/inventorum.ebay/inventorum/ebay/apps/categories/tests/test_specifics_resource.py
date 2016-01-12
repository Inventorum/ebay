# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.categories.serializers import CategorySpecificsSerializer
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestSpecificsResource(EbayAuthenticatedAPITestCase):

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

    def test_get_resource(self):
        leaf_category = self._build_leaf_category_with_specifics()
        response = self.client.get('/categories/{pk}/specifics'.format(pk=leaf_category.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, CategorySpecificsSerializer(leaf_category.specifics.all(), many=True).data)
