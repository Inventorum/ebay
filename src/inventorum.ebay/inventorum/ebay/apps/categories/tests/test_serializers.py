# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.tests.testcases import UnitTestCase

from inventorum.ebay.apps.categories import serializers
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory

log = logging.getLogger(__name__)


class TestCategorySerializers(UnitTestCase):

    def test_serialization_of_root_with_children(self):
        root = CategoryFactory.create(name="Some root category",
                                      country="DE",
                                      parent=None)
        CategoryFactory.create(parent=root)

        subject = serializers.CategorySerializer(root)

        self.assertEqual(subject.data, {
            "id": root.id,
            "name": "Some root category",
            "country": "DE",
            "parent_id": None,
            "is_leaf": False
        })

    def test_serialization_of_leaf(self):
        parent = CategoryFactory.create()
        leaf = CategoryFactory.create(name="Some leaf category",
                                      country="DE",
                                      parent=parent)

        subject = serializers.CategorySerializer(leaf)

        self.assertEqual(subject.data, {
            "id": leaf.id,
            "name": "Some leaf category",
            "country": "DE",
            "parent_id": parent.id,
            "is_leaf": True
        })


class TestCategoryBreadcrumbSerializer(UnitTestCase):

    def test_serialization(self):
        category = CategoryFactory.create(name="Some category")

        subject = serializers.CategoryBreadcrumbSerializer(category)

        self.assertEqual(subject.data, {
            "id": category.id,
            "name": "Some category"
        })
