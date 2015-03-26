# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.tests.testcases import APITestCase


log = logging.getLogger(__name__)


class TestProductPublish(APITestCase):

    def test_first_time_publish(self):
        product_id = 1
        response = self.client.post("/products/%s/publish" % product_id)
        self.assertEqual(response.status_code, 200)
