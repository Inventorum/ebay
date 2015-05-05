# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta

from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum.ebay.apps.core_api import BinaryCoreOrderStates
from inventorum.ebay.apps.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.apps.core_api.tests.factories import CoreOrderFactory
from inventorum.ebay.apps.orders.core_orders_sync import CoreOrdersSync
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory
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

        core_order_syncer = "inventorum.ebay.apps.orders.core_orders_sync.CoreOrderSyncer.__call__"
        self.core_order_syncer_mock = self.patch(core_order_syncer)

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

        self.assertTrue(self.core_api_mock.get_paginated_orders_delta.called)
        self.core_api_mock.get_paginated_orders_delta.assert_called_once_with(start_date=self.account.time_added)
        self.assertFalse(self.core_order_syncer_mock.called)

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

    def test_invokes_syncer_with_correct_params(self):
        order_1 = OrderModelFactory.create(inv_id=1)
        core_order_1 = CoreOrderFactory.create(id=order_1.inv_id, state=BinaryCoreOrderStates.PENDING)

        order_2 = OrderModelFactory.create(inv_id=2)
        core_order_2 = CoreOrderFactory.create(id=order_2.inv_id, state=BinaryCoreOrderStates.PENDING)

        self.expect_modified_orders([core_order_1, core_order_2])

        subject = CoreOrdersSync(account=self.account)
        subject.run()

        self.assertEqual(self.core_order_syncer_mock.call_count, 2)

        first_call_args, first_call_kwargs = self.core_order_syncer_mock.call_args_list[0]
        self.assertEqual(first_call_args[0], order_1)
        self.assertEqual(first_call_args[1], core_order_1)

        second_call_args, second_call_kwargs = self.core_order_syncer_mock.call_args_list[1]
        self.assertEqual(second_call_args[0], order_2)
        self.assertEqual(second_call_args[1], core_order_2)
