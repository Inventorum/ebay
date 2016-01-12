# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.lib.core_api import PaginatedFakeCoreAPIResponse
from inventorum_ebay.lib.core_api.pager import Pager
from inventorum_ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestPager(UnitTestCase):

    class FakeCoreAPIClient(object):

        def __init__(self, responses_by_page_number):
            self._responses_by_page_number = responses_by_page_number

            self.last_requested_path = None
            self.last_requested_params = None

        def get(self, path, params=None, custom_headers=None):
            self.last_requested_path = path
            self.last_requested_params = params

            assert "page" in params
            page_number = params["page"]
            return self._responses_by_page_number[page_number]

    def test_with_empty_page(self):
        fake_responses_by_page = {
            1: self.make_valid_response(total=0, data=[])
        }
        fake_client = self.FakeCoreAPIClient(fake_responses_by_page)

        subject = Pager(client=fake_client, path="/api/products", limit_per_page=100)

        # assert initial request
        self.assertEqual(fake_client.last_requested_path, "/api/products")
        self.assertEqual(fake_client.last_requested_params, {
            "page": 1,
            "limit": 100
        })

        self.assertEqual(subject.total_items, 0)
        self.assertEqual(subject.total_pages, 1)

        pages = list(subject.pages)
        self.assertEqual(len(pages), 1)

        self.assert_page(pages[0], expected_number=1, expected_response=fake_responses_by_page[1], expected_data=[])

    def test_with_single_and_limit_reaching_page(self):
        fake_responses_by_page = {
            1: self.make_valid_response(total=2, data=[{"id": 1}, {"id": 2}])
        }
        fake_client = self.FakeCoreAPIClient(fake_responses_by_page)

        subject = Pager(client=fake_client, path="/api/products", limit_per_page=2)

        # assert initial request
        self.assertEqual(fake_client.last_requested_path, "/api/products")
        self.assertEqual(fake_client.last_requested_params, {
            "page": 1,
            "limit": 2
        })

        self.assertEqual(subject.total_items, 2)
        self.assertEqual(subject.total_pages, 1)

        pages = list(subject.pages)
        self.assertEqual(len(pages), 1)

        self.assert_page(pages[0], expected_number=1, expected_response=fake_responses_by_page[1],
                         expected_data=[{"id": 1}, {"id": 2}])

    def test_with_multiple_pages(self):
        fake_responses_by_page = {
            1: self.make_valid_response(total=5, data=[{"id": 1}, {"id": 2}]),
            2: self.make_valid_response(total=5, data=[{"id": 3}, {"id": 4}]),
            3: self.make_valid_response(total=5, data=[{"id": 5}])
        }
        fake_client = self.FakeCoreAPIClient(fake_responses_by_page)

        subject = Pager(client=fake_client, path="/api/products", limit_per_page=2)

        # assert initial request
        self.assertEqual(fake_client.last_requested_path, "/api/products")
        self.assertEqual(fake_client.last_requested_params, {
            "page": 1,
            "limit": 2
        })

        self.assertEqual(subject.total_items, 5)
        self.assertEqual(subject.total_pages, 3)

        pages = list(subject.pages)
        self.assertEqual(len(pages), 3)

        self.assert_page(pages[0], expected_number=1, expected_response=fake_responses_by_page[1],
                         expected_data=[{"id": 1}, {"id": 2}])

        self.assert_page(pages[1], expected_number=2, expected_response=fake_responses_by_page[2],
                         expected_data=[{"id": 3}, {"id": 4}])

        self.assert_page(pages[2], expected_number=3, expected_response=fake_responses_by_page[3],
                         expected_data=[{"id": 5}])

    def test_with_multiple_limit_reaching_pages(self):
        total = 1000
        limit_per_page = 100

        # 10 pages with 100 items
        fake_responses_by_page = {p: self.make_valid_response(total, [{"id": i, "x": "y"} for i in range(1, 100 + 1)])
                                  for p in range(1, 10 + 1)}

        fake_client = self.FakeCoreAPIClient(fake_responses_by_page)

        subject = Pager(client=fake_client, path="/api/products", limit_per_page=limit_per_page)

        # assert initial request
        self.assertEqual(fake_client.last_requested_path, "/api/products")
        self.assertEqual(fake_client.last_requested_params, {
            "page": 1,
            "limit": limit_per_page
        })

        for i, page in enumerate(subject.pages):
            page_number = i + 1

            if page_number > 1:
                self.assertEqual(fake_client.last_requested_path, "/api/products")
                self.assertEqual(fake_client.last_requested_params, {
                    "page": page_number,
                    "limit": limit_per_page
                })

            self.assert_page(page, expected_number=page_number, expected_response=fake_responses_by_page[page_number],
                             expected_data=fake_responses_by_page[page_number].json().get("data"))

    def make_valid_response(self, total, data):
        return PaginatedFakeCoreAPIResponse(total=total, data=data)

    def assert_page(self, page, expected_number, expected_response, expected_data):
        self.assertEqual(page.number, expected_number)
        self.assertEqual(page.response, expected_response)
        self.assertEqual(page.data, expected_data)
