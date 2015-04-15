# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging
from django.forms.models import model_to_dict
from django.utils.functional import cached_property
from inventorum.ebay.apps.categories.serializers import CategoryBreadcrumbSerializer
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.serializers import EbayProductCategorySerializer, EbayProductSerializer
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.tests import Countries
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestEbayCategorySerializer(UnitTestCase):

    def test_serialize(self):
        root_category = CategoryFactory.create(name="Root category")
        level_2_category = CategoryFactory.create(name="Level 2 category", parent=root_category)
        leaf_category = CategoryFactory.create(name="Leaf category", parent=level_2_category)

        subject = EbayProductCategorySerializer(leaf_category)

        self.assertEqual(subject.data, {
            "id": leaf_category.id,
            "name": "Leaf category",
            "country": "DE",
            "parent_id": level_2_category.id,
            "is_leaf": True,
            "breadcrumb": [
                {"id": root_category.id, "name": "Root category"},
                {"id": level_2_category.id, "name": "Level 2 category"}
            ]
        })


# TODO: Test for published product (create factory for items)
class TestEbayProductSerializer(UnitTestCase):

    @cached_property
    def some_category_with_parent(self):
        some_parent = CategoryFactory.create(name="Some parent")
        return CategoryFactory.create(name="Some category", parent=some_parent)

    def test_serialize(self):
        category = self.some_category_with_parent
        product = EbayProductFactory.create(category=category)

        subject = EbayProductSerializer(product)

        self.assertEqual(subject.data, {
            "id": product.id,
            "listing_url": None,
            "is_published": False,
            "category": {
                "id": category.id,
                "name": "Some category",
                "country": "DE",
                "parent_id": category.parent_id,
                "is_leaf": True,
                "breadcrumb": [{"id": category.parent_id, "name": "Some parent"}]
            }
        })

    def test_deserialize_serialized(self):
        category = self.some_category_with_parent
        product = EbayProductFactory(category=category)

        serialized = EbayProductSerializer(product).data

        subject = EbayProductSerializer(product, data=serialized)
        subject.is_valid(raise_exception=True)
        subject.save()

        product.reload()

        # deserialize serialized doesn't change the representation
        data_before = serialized
        self.assertEqual(EbayProductSerializer(product).data, data_before)

    def test_category_validation(self):
        def get_partial_data_for_category_update(category):
            return {
                "category": {
                    "id": category.id
                }
            }

        root_category = CategoryFactory.create(name="Root category")
        level_2_category = CategoryFactory.create(name="Level 2 category", parent=root_category)
        leaf_category = CategoryFactory.create(name="Leaf category", parent=level_2_category)

        product = EbayProductFactory(category=None)

        # try to assign category without id
        invalid_data = {"category": {}}
        subject = EbayProductSerializer(product, data=invalid_data, partial=True)
        self.assertFalse(subject.is_valid())
        self.assertEqual(subject.errors["category"], ['id is required'])

        # try to assign non-existing category
        non_persistent_category = CategoryFactory.build(id=999999)
        invalid_data = get_partial_data_for_category_update(non_persistent_category)
        subject = EbayProductSerializer(product, data=invalid_data, partial=True)
        self.assertFalse(subject.is_valid())
        self.assertEqual(subject.errors["category"], ['Invalid pk "999999" - object does not exist.'])

        # try to assign non-leaf categories
        for category in [root_category, level_2_category]:
            invalid_data = get_partial_data_for_category_update(category)
            subject = EbayProductSerializer(product, data=invalid_data, partial=True)
            self.assertFalse(subject.is_valid())
            self.assertEqual(subject.errors["category"], ["Given category is not a leaf"])

        valid_data = get_partial_data_for_category_update(leaf_category)
        assert leaf_category.is_leaf_node()
        subject = EbayProductSerializer(product, data=valid_data, partial=True)
        subject.is_valid(raise_exception=True)

        # try to assign categories from different country
        assert product.account.country != Countries.AT
        leaf_category.country = Countries.AT
        leaf_category.save()
        leaf_category_different_country = leaf_category

        invalid_data = get_partial_data_for_category_update(leaf_category_different_country)
        subject = EbayProductSerializer(product, data=invalid_data, partial=True)
        self.assertFalse(subject.is_valid())
        self.assertEqual(subject.errors["category"], ["Invalid category"])
