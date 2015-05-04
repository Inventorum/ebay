# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta

from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.apps.orders.core_orders_sync import CoreOrdersSync
from inventorum.ebay.tests.testcases import UnitTestCase
from mock import PropertyMock


log = logging.getLogger(__name__)


class UnitTestCoreOrdersSync(UnitTestCase):

    def setUp(self):
        super(UnitTestCoreOrdersSync, self).setUp()

        # account with default user
        self.default_user = EbayUserFactory.create()
        self.account = self.default_user.account

        self.create_mocks()

    def create_mocks(self):
        core_api = "inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api"
        self.core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))

    def reset_mocks(self):
        self.core_api_mock.reset_mock()

    def expect_modified_orders(self, *pages):
        mock = self.core_api_mock.get_paginated_orders_delta
        mock.reset_mock()
        mock.return_value = iter(pages)

    def test_basic_logic_with_empty_delta(self):
        assert self.account.last_core_orders_sync is None

        self.expect_modified_orders([])

        subject = CoreOrdersSync(account=self.account)
        subject.run()

        self.core_api_mock.get_paginated_orders_delta.assert_called_once_with(start_date=self.account.time_added)

        self.assertIsNotNone(self.account.last_core_orders_sync)
        self.assertTrue(datetime.utcnow() - self.account.last_core_orders_sync < timedelta(seconds=1))

        # next sync for the account should start from last_core_orders_sync
        self.reset_mocks()

        self.expect_modified_orders([])

        # reload changes from database
        self.account = self.account.reload()

        last_core_orders_sync = self.account.last_core_orders_sync

        subject = CoreOrdersSync(account=self.account)
        subject.run()

        self.core_api_mock.get_paginated_orders_delta.assert_called_once_with(start_date=last_core_orders_sync)
