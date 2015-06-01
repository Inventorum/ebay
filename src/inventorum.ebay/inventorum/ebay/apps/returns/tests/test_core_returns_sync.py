# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.returns.core_returns_sync import CoreReturnsSync
from inventorum.ebay.lib.celery import celery_test_case
from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.lib.core_api.tests.factories import CoreDeltaReturnFactory
from inventorum.ebay.tests.testcases import UnitTestCase, EbayAuthenticatedAPITestCase
from mock import PropertyMock


log = logging.getLogger(__name__)


class IntegrationTestPeriodicCoreReturnsSync(EbayAuthenticatedAPITestCase):

    @celery_test_case()
    def xxxtest_integration(self):
        product_id = StagingTestAccount.Products.IPAD_STAND

        # create test order
        ebay_order = OrderModelFactory.create()
        OrderLineItemModelFactory.create(order=ebay_order,
                                         orderable_item__product__inv_id=product_id,
                                         quantity=5)
        core_order_creation_data = OrderModelCoreAPIDataSerializer(ebay_order).data
        # create closed ebay order to be able to make returns
        core_order_creation_data["state"] |= BinaryCoreOrderStates.CLOSED
        core_order = self.account.core_api.create_order(data=core_order_creation_data)
        core_order_line_item = core_order.basket.items[0]

        # create return
        return_quantity = int(core_order_line_item.quantity) - 1
        core_return_creation_data = {"items": [{"item": core_order_line_item.id,
                                                "quantity": return_quantity}],
                                     "returnType": 1}
        log.info(core_order_creation_data)
        core_return_id = self.account.core_api.returns.create(order_id=core_order.id, data=core_return_creation_data)
        log.info(core_return_id)

        pages = self.account.core_api.returns.get_paginated_delta(start_date=datetime.now() - timedelta(days=1))
        for page in pages:
            for core_return in page:
                log.info(core_return.id)
                log.info(core_return.items[0].id)
                log.info(core_return.items[0].name)


class UnitTestCoreReturnsSync(UnitTestCase):

    def setUp(self):
        super(UnitTestCoreReturnsSync, self).setUp()

        # account with default user
        self.default_user = EbayUserFactory.create()
        self.account = self.default_user.account

        self.create_mocks()

    def create_mocks(self):
        core_api = "inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api"
        self.core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))

        core_return_syncer = "inventorum.ebay.apps.returns.core_returns_sync.CoreReturnSyncer.__call__"
        self.core_return_syncer_mock = self.patch(core_return_syncer)

    def reset_mocks(self):
        self.core_api_mock.reset_mock()

    def expect_core_returns(self, *pages):
        mock = self.core_api_mock.returns.get_paginated_delta
        mock.reset_mock()
        mock.return_value = iter(pages)

    def test_basic_logic_with_empty_delta(self):
        assert self.account.last_core_returns_sync is None

        self.expect_core_returns([])

        subject = CoreReturnsSync(account=self.account)
        subject.run()

        self.assertTrue(self.core_api_mock.returns.get_paginated_delta.called)
        self.core_api_mock.returns.get_paginated_delta.assert_called_once_with(start_date=self.account.time_added)
        self.assertFalse(self.core_return_syncer_mock.called)

        self.assertIsNotNone(self.account.last_core_returns_sync)
        self.assertTrue(datetime.utcnow() - self.account.last_core_returns_sync < timedelta(seconds=1))

        # next sync for the account should start from last_core_returns_sync
        self.reset_mocks()

        self.expect_core_returns([])

        # reload changes from database
        self.account = self.account.reload()

        last_core_returns_sync = self.account.last_core_returns_sync

        subject = CoreReturnsSync(account=self.account)
        subject.run()

        self.core_api_mock.returns.get_paginated_delta.assert_called_once_with(start_date=last_core_returns_sync)

    def test_invokes_syncer_with_correct_params(self):
        core_return_1 = CoreDeltaReturnFactory.create()
        core_return_2 = CoreDeltaReturnFactory.create()

        self.expect_core_returns([core_return_1, core_return_2])

        subject = CoreReturnsSync(account=self.account)
        subject.run()

        self.assertEqual(self.core_return_syncer_mock.call_count, 2)

        first_call_args, first_call_kwargs = self.core_return_syncer_mock.call_args_list[0]
        self.assertEqual(first_call_args[0], core_return_1)

        second_call_args, second_call_kwargs = self.core_return_syncer_mock.call_args_list[1]
        self.assertEqual(second_call_args[0], core_return_2)
