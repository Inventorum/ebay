from __future__ import absolute_import, unicode_literals
from inventorum_ebay.apps.items import EbaySKU
from inventorum_ebay.tests.testcases import UnitTestCase


class UnitTestsForEbaySKU(UnitTestCase):

    def setUp(self):
        self.sku = 'invtest_1234'
        self.wrong_sku = 'invstaging_1234'

    def test_get_env_prefix(self):
        self.assertEquals(EbaySKU.get_env_prefix(), 'invtest_')

    def test_extract_product_id(self):
        self.assertEqual(EbaySKU.extract_product_id(self.sku), '1234')

    # The current environment for tests will always be the test environment. The configuration can be find in test.ini
    def test_belongs_to_current_env(self):
        self.assertTrue(EbaySKU.belongs_to_current_env(self.sku))

    def test_wrong_case_for_belongs_to_current_env(self):
        self.assertFalse(EbaySKU.belongs_to_current_env(self.wrong_sku))

    def test_generate_sku(self):
        self.assertEquals(EbaySKU.generate_sku(1234), 'invtest_1234')
