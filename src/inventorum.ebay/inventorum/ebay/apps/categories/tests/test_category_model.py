# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.tests.testcases import APITestCase


class TestCategoryModel(APITestCase):
    def test_it(self):
        category = CategoryModel.objects.create(
            name="Test",
            external_id="123",
            external_parent_id=None,
            country="DE"
        )

        self.assertEqual(CategoryModel.objects.count(), 1)

        category.delete()

        self.assertEqual(CategoryModel.objects.count(), 0)
        self.assertEqual(CategoryModel.admin_objects.count(), 1)

    def test_tree_manager(self):
        category = CategoryModel.objects.create(
            name="Test",
            external_id="123",
            external_parent_id=None,
            country="DE"
        )

        self.assertEqual(CategoryModel.tree_objects.count(), 1)

        category.delete()

        self.assertEqual(CategoryModel.tree_objects.count(), 0)
        self.assertEqual(CategoryModel.admin_objects.count(), 1)