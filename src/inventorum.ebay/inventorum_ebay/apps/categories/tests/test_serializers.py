# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum_ebay.apps.categories.serializers import CategorySpecificsSerializer
from inventorum_ebay.tests import Countries

from inventorum_ebay.tests.testcases import UnitTestCase

from inventorum_ebay.apps.categories import serializers
from inventorum_ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory

log = logging.getLogger(__name__)


class TestCategorySerializers(UnitTestCase):

    def test_serialization_of_root_with_children(self):
        root = CategoryFactory.create(name="Some root category",
                                      country=Countries.DE,
                                      parent=None)
        CategoryFactory.create(parent=root)

        subject = serializers.CategorySerializer(root)

        self.assertEqual(subject.data, {
            "id": root.id,
            "name": "Some root category",
            "country": "DE",
            "parent_id": None,
            "is_leaf": False,
            "variations_enabled": False,
            "ean_enabled": False,
            "ean_required": False
        })

    def test_serialization_of_leaf(self):
        parent = CategoryFactory.create()
        leaf = CategoryFactory.create(name="Some leaf category",
                                      country=Countries.AT,
                                      parent=parent)

        subject = serializers.CategorySerializer(leaf)

        self.assertEqual(subject.data, {
            "id": leaf.id,
            "name": "Some leaf category",
            "country": "AT",
            "parent_id": parent.id,
            "is_leaf": True,
            "variations_enabled": False,
            "ean_enabled": False,
            "ean_required": False
        })

    def test_ean_enabled_and_required(self):
        category = CategoryFactory.create(name="Some category",
                                          country=Countries.AT,
                                          features__ean_enabled=True)

        self.assertPrecondition(category.features.ean_enabled, True)
        self.assertPrecondition(category.features.ean_required, False)

        subject = serializers.CategorySerializer(category)
        self.assertTrue(subject.data["ean_enabled"])
        self.assertFalse(subject.data["ean_required"])

        category.features.ean_required = True

        subject = serializers.CategorySerializer(category)
        self.assertTrue(subject.data["ean_enabled"])
        self.assertTrue(subject.data["ean_required"])


class TestCategoryBreadcrumbSerializer(UnitTestCase):

    def test_serialization(self):
        category = CategoryFactory.create(name="Some category")

        subject = serializers.CategoryBreadcrumbSerializer(category)

        self.assertEqual(subject.data, {
            "id": category.id,
            "name": "Some category"
        })


class TestCategorySpecificsSerializer(UnitTestCase):

    def test_serialization(self):
        category = CategoryFactory.create(name="Some category")

        specific = CategorySpecificFactory.create(category=category)
        required_specific = CategorySpecificFactory.create_required(category=category)

        specific_data = CategorySpecificsSerializer(specific).data
        self.assertEqual(specific_data, {
            'can_use_own_values': True,
            'can_use_in_variations': True,
            'help_url': specific.help_url,
            'help_text': specific.help_text,
            'is_required': False,
            'min_values': 0,
            'max_values': 1,
            'name': specific.name,
            'id': specific.id,
            'values': [{'value': v.value} for v in specific.values.all()]
        })

        required_specific_data = CategorySpecificsSerializer(required_specific).data
        self.assertEqual(required_specific_data['is_required'], True)



