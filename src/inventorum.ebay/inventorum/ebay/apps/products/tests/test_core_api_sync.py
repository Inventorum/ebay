# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.core_api.tests import CoreApiTestHelpers
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class IntegrationTestCoreAPISync(EbayAuthenticatedAPITestCase, CoreApiTestHelpers):

    def test_integration(self):
        inv_id = self.create_core_api_product(name="Test product 1", gross_price="1.99", quantity=12)
