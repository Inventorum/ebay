# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime, timedelta
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory
from inventorum.ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, EbayItemFactory
from inventorum.ebay.apps.returns.core_returns_sync import CoreReturnsSync, CoreReturnSyncer
from inventorum.ebay.apps.returns.tasks import periodic_core_returns_sync_task
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.celery import celery_test_case
from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.tests import StagingTestAccount, ApiTest
from inventorum.ebay.lib.core_api.tests.factories import CoreDeltaReturnFactory, CoreDeltaReturnItemFactory
from inventorum.ebay.tests.testcases import UnitTestCase, EbayAuthenticatedAPITestCase
from inventorum.util.celery import get_anonymous_task_execution_context, TaskExecutionContext
from mock import PropertyMock


log = logging.getLogger(__name__)


class IntegrationTestPeriodicCoreReturnsSync(EbayAuthenticatedAPITestCase, ShippingServiceTestMixin):

    @celery_test_case()
    @ApiTest.use_cassette("periodic_core_returns_sync.yaml", filter_query_parameters=['start_date'], record_mode="never")
    def test_integration(self):
        product = EbayProductFactory.create(inv_id=StagingTestAccount.Products.IPAD_STAND)

        ebay_order_regular, core_return_id_regular = \
            self._create_order_with_immediate_core_return(product, is_click_and_collect=False)

        ebay_order_click_and_collect, core_return_id_click_and_collect = \
            self._create_order_with_immediate_core_return(product, is_click_and_collect=True)

        periodic_core_returns_sync_task.delay(context=get_anonymous_task_execution_context())

    def _create_order_with_immediate_core_return(self, product, is_click_and_collect):
        """
        :type product: inventorum.ebay.apps.products.models.EbayProductModel
        :type is_click_and_collect: bool

        :rtype: (inventorum.ebay.apps.orders.models.OrderModel, int)
        :returns: order model instance and core return id
        """
        order_extra = {}
        if is_click_and_collect:
            order_extra["selected_shipping__service"] = self.get_shipping_service_click_and_collect()

        order = OrderModelFactory.create()
        OrderLineItemModelFactory.create(order=order,
                                         orderable_item__product=product,
                                         quantity=5)

        core_order_creation_data = OrderModelCoreAPIDataSerializer(order).data
        # create closed ebay order to be able to make returns
        core_order_creation_data["state"] |= BinaryCoreOrderStates.CLOSED
        core_order = self.account.core_api.create_order(data=core_order_creation_data)
        core_order_line_item = core_order.basket.items[0]

        # create return
        return_quantity = int(core_order_line_item.quantity) - 1
        core_return_creation_data = {"items": [{"item": core_order_line_item.id,
                                                "quantity": return_quantity}],
                                     "returnType": 1}
        core_return_id = self.account.core_api.returns.create(order_id=core_order.id, data=core_return_creation_data)

        return order, core_return_id


class UnitTestCoreReturnsSync(UnitTestCase):

    def setUp(self):
        super(UnitTestCoreReturnsSync, self).setUp()

        # account with default user
        self.account = EbayUserFactory.create().account

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
        order_1 = OrderModelFactory.create(inv_id=23, account=self.account)
        core_return_1 = CoreDeltaReturnFactory.create(order_id=23)

        order_2 = OrderModelFactory.create(inv_id=42, account=self.account)
        core_return_2 = CoreDeltaReturnFactory.create(order_id=42)

        self.expect_core_returns([core_return_1, core_return_2])

        subject = CoreReturnsSync(account=self.account)
        subject.run()

        self.assertEqual(self.core_return_syncer_mock.call_count, 2)

        first_call_args, first_call_kwargs = self.core_return_syncer_mock.call_args_list[0]
        self.assertEqual(first_call_args[0], core_return_1)
        self.assertEqual(first_call_args[1], order_1)

        second_call_args, second_call_kwargs = self.core_return_syncer_mock.call_args_list[1]
        self.assertEqual(second_call_args[0], core_return_2)
        self.assertEqual(second_call_args[1], order_2)

    def test_account_scope_and_returns_for_unknown_orders(self):
        # create order for different account
        different_account = EbayUserFactory.create().account
        OrderModelFactory.create(inv_id=23, account=different_account)

        # return for different account order must not be synced
        core_return_1 = CoreDeltaReturnFactory.create(order_id=23)
        # return for unknown order must not be synced
        core_return_2 = CoreDeltaReturnFactory.create(order_id=666)

        self.expect_core_returns([core_return_1, core_return_2])

        subject = CoreReturnsSync(account=self.account)
        subject.run()

        self.assertEqual(self.core_return_syncer_mock.call_count, 0)


class UnitTestCoreReturnSyncer(UnitTestCase, ShippingServiceTestMixin):

    def setUp(self):
        super(UnitTestCoreReturnSyncer, self).setUp()

        self.account = EbayAccountFactory.create()
        self.default_user = EbayUserFactory.create(account=self.account)

        # syncer is state-less, no need to regenerate it
        self.sync = CoreReturnSyncer(account=self.account)

        self.setup_mocks()

    def setup_mocks(self):
        pass

    def reset_mocks(self):
        pass

    def create_order(self, ebay_item, quantity, is_click_and_collect):
        """
        :type ebay_item: inventorum.ebay.apps.products.models.EbayItemModel
        :type quantity: int
        :type is_click_and_collect: bool

        :rtype: inventorum.ebay.apps.orders.models.OrderModel
        """
        order_extra = {}
        if is_click_and_collect:
            order_extra["selected_shipping__service"] = self.get_shipping_service_click_and_collect()

        order = OrderModelFactory.create(inv_id=1000, **order_extra)

        OrderLineItemModelFactory.create(inv_id=2000,
                                         order=order,
                                         orderable_item=ebay_item,
                                         quantity=quantity)

        return order

    def create_core_return(self, order, quantity):
        """
        :type order: inventorum.ebay.apps.orders.models.OrderModel
        :type quantity: int

        :rtype: inventorum.ebay.lib.core_api.models.CoreDeltaReturn
        """
        order_line_item = order.line_items.first()

        return_item = CoreDeltaReturnItemFactory.create(basket_item_id=order_line_item.inv_id,
                                                        quantity=quantity,
                                                        name=order_line_item.name)
        return CoreDeltaReturnFactory(order_id=order.inv_id, items=[return_item])

    def test_task_execution_context(self):
        self.assertEqual(self.sync.get_task_execution_context(),
                         TaskExecutionContext(user_id=self.default_user.id,
                                              account_id=self.account.id,
                                              request_id=None))

    def test_handles_click_and_collect_returns_correctly(self):
        ebay_item = EbayItemFactory()
        order = self.create_order(ebay_item, quantity=5, is_click_and_collect=True)

        core_return = self.create_core_return(order, quantity=3)

        self.sync(core_return, order)

    def test_does_not_handle_non_click_and_collect_returns(self):
        ebay_item = EbayItemFactory()
        order = self.create_order(ebay_item, quantity=1, is_click_and_collect=False)

        core_return = self.create_core_return(order, quantity=1)

        self.sync(core_return, order)
