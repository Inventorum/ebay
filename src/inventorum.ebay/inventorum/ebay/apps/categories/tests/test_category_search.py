# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import json
import logging
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory
from inventorum.ebay.apps.categories.search import CategorySearchService

from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.tests.testcases import UnitTestCase, EbayAuthenticatedAPITestCase
from rest_framework import status


log = logging.getLogger(__name__)


class CategoryTestMixin(object):

    def create_apple_category_tree(self):
        # Mobile & Communication > Mobile Phones without Contract
        self.category_mobiles = CategoryFactory.create(name="Mobile & Communication")
        self.category_mobiles_without_contract = CategoryFactory.create(name="Mobile Phones without Contract",
                                                                        external_id="9355",
                                                                        parent=self.category_mobiles)

        # Computer, Tablets & Network > Desktop Computers > Apple Desktops & All-in-Ones
        self.category_computers = CategoryFactory.create(name="Computer, Tablets & Network")

        self.category_desktop_computers = CategoryFactory.create(name="Desktop Computers",
                                                                 parent=self.category_computers)

        self.category_apple_desktops = CategoryFactory.create(name="Apple Desktops & All-in-Ones",
                                                              external_id="111418",
                                                              parent=self.category_desktop_computers)

        # Computer, Tablets & Network > Notebooks & Netbooks > Apple Notebooks
        self.category_notebooks = CategoryFactory.create(name="Notebooks & Netbooks",
                                                         parent=self.category_computers)

        self.category_apple_notebooks = CategoryFactory.create(name="Apple Notebooks",
                                                               external_id="111422",
                                                               parent=self.category_notebooks)

        # TV, Video & Audio > Internet-TV & Media Streamer
        self.category_tv = CategoryFactory.create(name="TV, Video & Audio")
        self.category_apple_internet_tv = CategoryFactory.create(name="Apple Internet-TV & Media Streamer",
                                                                 external_id="168058",
                                                                 parent=self.category_tv)


class TestCategorySearchResource(EbayAuthenticatedAPITestCase, CategoryTestMixin):

    def setUp(self):
        super(TestCategorySearchResource, self).setUp()

        # create some test categories
        self.create_apple_category_tree()

    def request_search(self, query, limit=None):
        """
        :type query: unicode
        :type limit: int
        :rtype: rest_framework.response.Response
        """
        query_string = "query={}".format(query)
        if limit is not None:
            query_string += "&limit={}".format(limit)

        response = self.client.get("/categories/search?{}".format(query_string))
        self.assertPrecondition(response.status_code, status.HTTP_200_OK)

        return response

    def test_no_results(self):
        response = self.request_search(query="NO RESULTS")
        self.assertEqual(response.data, [])

    def test_search_and_serializer(self):
        response = self.request_search(query="Apple")

        results = response.data
        self.assertEqual(len(results), 2)

        rooted_result_1 = results[0]
        self.assertEqual(rooted_result_1, {"root": {"id": self.category_computers.id,
                                                    "name": "Computer, Tablets & Network",
                                                    "country": "DE",
                                                    "parent_id": None,
                                                    "is_leaf": False,
                                                    "variations_enabled": False},
                                           "categories": [{"id": self.category_apple_desktops.id,
                                                           "name": "Apple Desktops & All-in-Ones",
                                                           "country": "DE",
                                                           "parent_id": self.category_desktop_computers.id,
                                                           "is_leaf": True,
                                                           "variations_enabled": False,
                                                           "breadcrumbs": [{"id": self.category_computers.id,
                                                                            "name": "Computer, Tablets & Network"},
                                                                           {"id": self.category_desktop_computers.id,
                                                                            "name": "Desktop Computers"}]},
                                                          {"id": self.category_apple_notebooks.id,
                                                           "name": "Apple Notebooks",
                                                           "country": "DE",
                                                           "parent_id": self.category_notebooks.id,
                                                           "is_leaf": True,
                                                           "variations_enabled": False,
                                                           "breadcrumbs": [{"id": self.category_computers.id,
                                                                            "name": "Computer, Tablets & Network"},
                                                                           {"id": self.category_notebooks.id,
                                                                            "name": "Notebooks & Netbooks"}]}]})

        rooted_result_2 = results[1]
        self.assertEqual(rooted_result_2["root"]["name"], "TV, Video & Audio")
        self.assertItemsEqual([c["id"] for c in rooted_result_2["categories"]],
                              [self.category_apple_internet_tv.id])

    def test_limit(self):
        response = self.request_search(query="Apple", limit=1)
        results = response.data
        self.assertEqual(len(results), 1)

    def test_missing_query_param(self):
        response = self.client.get("/categories/search")
        self.assertEqual(response.data, {"query": ["This field is required."]})


class TestCategorySearchService(UnitTestCase, CategoryTestMixin):

    def setUp(self):
        super(TestCategorySearchService, self).setUp()

        self.account = EbayAccountFactory.create()

        # Invariant: default country of categories must equal account category since categories are filtered by country
        assert self.account.country == CategoryFactory.country

        # create some test categories
        self.create_apple_category_tree()

        self.subject = CategorySearchService(self.account)

    def test_without_results(self):
        categories = self.subject.search(query="WAT")
        self.assertEqual(categories.count(), 0)

    def test_only_searches_leafs(self):
        categories = self.subject.search(query="Desktop")
        self.assertEqual(categories.count(), 1)
        self.assertItemsEqual(categories, [self.category_apple_desktops])

    def test_with_multiple_results(self):
        categories = self.subject.search(query="Apple")
        self.assertEqual(categories.count(), 3)
        self.assertItemsEqual(categories, [self.category_apple_desktops, self.category_apple_notebooks,
                                           self.category_apple_internet_tv])

    def test_limit(self):
        categories = self.subject.search(query="Apple", limit=1)
        self.assertEqual(categories.count(), 1)

    def test_result_grouping_by_root(self):
        rooted_results = self.subject.search_and_group_results_by_root(query="Apple")
        self.assertEqual(len(rooted_results), 2)

        rooted_result_1 = rooted_results[0]
        self.assertEqual(rooted_result_1.root, self.category_computers)
        self.assertItemsEqual(rooted_result_1.categories, [self.category_apple_desktops, self.category_apple_notebooks])

        rooted_result_2 = rooted_results[1]
        self.assertEqual(rooted_result_2.root, self.category_tv)
        self.assertItemsEqual(rooted_result_2.categories, [self.category_apple_internet_tv])
