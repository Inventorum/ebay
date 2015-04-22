# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.apps.categories.serializers import CategorySerializer, CategoryBreadcrumbSerializer
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.tests import Countries
from rest_framework import status
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestCategoryList(EbayAuthenticatedAPITestCase):

    def setUp(self):
        super(TestCategoryList, self).setUp()

        # Invariant: default country of categories must equal account category since categories are filtered by country
        assert self.account.country == CategoryFactory.country

    def test_without_parent_id_returns_all_root_categories_by_country(self):
        # this test also asserts the complete response format and the correct ordering
        root_a = CategoryFactory.create(name="z root category")
        root_b = CategoryFactory.create(name="a root category")
        root_c = CategoryFactory.create(name="m root category")

        # some children that may not be included
        CategoryFactory.create(parent=root_a)
        CategoryFactory.create(parent=root_b)

        # some roots for other countries that may not be included
        assert CategoryFactory.country is not Countries.AT
        CategoryFactory.create(country=Countries.AT)

        response = self.get_categories()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = CategorySerializer([root_b, root_c, root_a], many=True).data

        self.assertEqual(response.data, {
            "total": 3,
            "data": expected_data,
            "breadcrumbs": []
        })

    def test_with_parent_id_returns_all_children(self):
        root = CategoryFactory.create()
        parents = CategoryFactory.create_batch(2, parent=root)
        children = CategoryFactory.create_batch(3, parent=parents[0])
        # some children that may not be included
        CategoryFactory.create_batch(2, parent=parents[1])

        response = self.get_categories(parent_id=root.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_categories_in_response(response, parents)

        response = self.get_categories(parent_id=parents[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_categories_in_response(response, children)

        response = self.get_categories(parent_id=children[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_categories_in_response(response, [])

    def test_with_invalid_parent_id(self):
        non_existing_parent_id = 10001

        response = self.get_categories(parent_id=non_existing_parent_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["key"], "categories.invalid_parent_id")

        assert CategoryFactory.country is not Countries.AT
        category_of_different_country = CategoryFactory.create(country=Countries.AT)

        response = self.get_categories(parent_id=category_of_different_country.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["key"], "categories.invalid_parent_id")

    def test_breadcrumb(self):
        root = CategoryFactory.create(name="root")
        level_2 = CategoryFactory.create(name="level 2", parent=root)
        level_3 = CategoryFactory.create(name="level 3", parent=level_2)
        leaf = CategoryFactory.create(name="leaf", parent=level_3)

        response = self.get_categories(parent_id=root.id)
        self.assert_breadcrumb_in_response(response, [root])

        response = self.get_categories(parent_id=level_2.id)
        self.assert_breadcrumb_in_response(response, [root, level_2])

        response = self.get_categories(parent_id=level_3.id)
        self.assert_breadcrumb_in_response(response, [root, level_2, level_3])

    def get_categories(self, parent_id=None):
        params = {}
        if parent_id is not None:
            params['parent_id'] = parent_id

        return self.client.get("/categories/", data=params)

    def assert_categories_in_response(self, response, expected_categories):
        """
        :param response: The actual response
        :param expected_categories: The expected categories (order is irrelevant)
        :type expected_categories: list of CategoryModel
        """
        expected_category_data = CategorySerializer(expected_categories, many=True).data
        actual_category_data = response.data["data"]
        self.assertItemsEqual(actual_category_data, expected_category_data)

    def assert_breadcrumb_in_response(self, response, expected_breadrumb_categories):
        """
        :param response: The actual response
        :param expected_breadrumb_categories: The expected breadcrumb categories
        :type expected_breadrumb_categories: list of CategoryModel
        """
        expected_breadrumb_data = CategoryBreadcrumbSerializer(expected_breadrumb_categories, many=True).data
        actual_breadcrumb_data = response.data["breadcrumbs"]
        self.assertEqual(actual_breadcrumb_data, expected_breadrumb_data)
