from ebaysdk.trading import Connection
from inventorum_ebay.lib.ebay import EbayTrading
from inventorum_ebay.tests.testcases import UnitTestCase
from inventorum_ebay.tests.utils import PatchMixin
from mock import patch, Mock


class ConfigMocked(object):
    values = {}

    def set(self, key, value, force=False):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key, None)


class EbayClassTestCase(UnitTestCase, PatchMixin):
    def setUp(self):
        super(EbayClassTestCase, self).setUp()
        self.connection_mock = self.patch('inventorum_ebay.lib.ebay.TradingConnection', spec=True)

        # Swap class in EbayTrading but store original one!
        self.original_class = EbayTrading.default_connection_cls
        EbayTrading.default_connection_cls = self.connection_mock

        self.instance_mock = self.connection_mock.return_value

        self.config = ConfigMocked()
        self.instance_mock.config = self.config
        self.instance_mock.error.return_value = False
        self.instance_mock.response = {}

        self.execute_mock = Mock()
        self.execute_mock.error.return_value = False
        self.execute_mock.dict.return_value = {}
        self.instance_mock.execute.return_value = self.execute_mock

        self.class_parallel_mock = self.patch('inventorum_ebay.lib.ebay.Parallel', spec=True)
        self.parallel_mock = self.class_parallel_mock.return_value
        self.parallel_mock.error.return_value = False

    def tearDown(self):
        EbayTrading.default_connection_cls = self.original_class
        super(EbayClassTestCase, self).tearDown()
