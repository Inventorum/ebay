from ebaysdk.trading import Connection
from inventorum.ebay.tests.testcases import UnitTestCase
from mock import patch, Mock


class ConfigMocked(object):
    values = {}

    def set(self, key, value, force=False):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key, None)


class EbayClassTestCase(UnitTestCase):
    def setUp(self):
        super(EbayClassTestCase, self).setUp()
        self.connection_original = Connection
        self.patcher = patch('inventorum.ebay.lib.ebay.Connection', spec=True)
        self.connection_mock = self.patcher.start()
        self.instance_mock = self.connection_mock.return_value

        self.config = ConfigMocked()
        self.instance_mock.config = self.config
        self.instance_mock.error.return_value = False
        self.instance_mock.response = {}

        self.execute_mock = Mock()
        self.execute_mock.error.return_value = False
        self.execute_mock.dict.return_value = {}
        self.instance_mock.execute.return_value = self.execute_mock


        self.patcher_parallel = patch('inventorum.ebay.lib.ebay.Parallel', spec=True)
        self.class_parallel_mock = self.patcher_parallel.start()
        self.parallel_mock = self.class_parallel_mock.return_value
        self.parallel_mock.error.return_value = False

    def tearDown(self):
        self.patcher.stop()
        self.patcher_parallel.stop()
        super(EbayClassTestCase, self).tearDown()