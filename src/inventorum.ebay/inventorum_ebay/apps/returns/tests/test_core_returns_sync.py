# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime, timedelta
from inventorum_ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory
from inventorum_ebay.apps.orders.serializers import OrderModelCoreAPIDataSerializer
from inventorum_ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum_ebay.apps.products.tests.factories import EbayProductFactory, EbayItemFactory
from inventorum_ebay.apps.returns import EbayRefundType
from inventorum_ebay.apps.returns.core_returns_sync import CoreReturnsSync, CoreReturnSyncer
from inventorum_ebay.apps.returns.models import ReturnModel
from inventorum_ebay.apps.returns.tasks import periodic_core_returns_sync_task
from inventorum_ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum_ebay.lib.celery import celery_test_case
from inventorum_ebay.lib.core_api import BinaryCoreOrderStates
from inventorum_ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum_ebay.tests import StagingTestAccount, ApiTest
from inventorum_ebay.lib.core_api.tests.factories import CoreDeltaReturnFactory, CoreDeltaReturnItemFactory
from inventorum_ebay.lib.ebay.data.events import EbayEventReturned
from inventorum_ebay.tests.testcases import UnitTestCase, EbayAuthenticatedAPITestCase
from inventorum.util.celery import get_anonymous_task_execution_context, TaskExecutionContext
from mock import PropertyMock


log = logging.getLogger(__name__)


class IntegrationTestPeriodicCoreReturnsSync(EbayAuthenticatedAPITestCase, ShippingServiceTestMixin):

    def setUp(self):
        super(IntegrationTestPeriodicCoreReturnsSync, self).setUp()
        self.setup_mocks()

    def setup_mocks(self):
        self.ebay_inbound_events_publish_mock = \
            self.patch("inventorum_ebay.lib.ebay.events.EbayInboundEvents.publish")

    def reset_mocks(self):
        self.ebay_inbound_events_publish_mock.reset_mock()

    @celery_test_case()
    @ApiTest.use_cassette("periodic_core_returns_sync.yaml", filter_query_parameters=['start_date'], record_mode="never")
    def test_integration(self):
        product = EbayProductFactory.create(account=self.account, inv_id=StagingTestAccount.Products.IPAD_STAND)

        # non-click-and-collect order should not be handled
        self._create_order_with_immediate_core_return(product, is_click_and_collect=False)

        # click-and-collect order, should be handled
        ebay_order_click_and_collect, core_return_id_click_and_collect = \
            self._create_order_with_immediate_core_return(product, is_click_and_collect=True)
        ebay_order_click_and_collect_line_item = ebay_order_click_and_collect.line_items.first()

        returns = ReturnModel.objects.all()
        self.assertPrecondition(returns.count(), 0)

        periodic_core_returns_sync_task.delay(context=get_anonymous_task_execution_context())

        # assert that models have been created
        self.assertPostcondition(returns.count(), 1)
        return_model = returns.last()

        self.assertEqual(return_model.items.count(), 1)
        return_item = return_model.items.first()

        self.assertEqual(return_model.inv_id, core_return_id_click_and_collect)
        self.assertEqual(return_item.order_line_item, ebay_order_click_and_collect_line_item)

        # assert that correct event has been sent to ebay
        self.assertTrue(self.ebay_inbound_events_publish_mock.called)
        first_call_args, first_call_kwargs = self.ebay_inbound_events_publish_mock.call_args_list[0]
        event = first_call_args[0]

        self.assertIsInstance(event, EbayEventReturned)
        self.assertEqual(event.payload, {"ebayOrderId": ebay_order_click_and_collect.ebay_id,
                                         "notifierRefundNote": "",
                                         "notifierRefundType": "EBAY",
                                         "notifierTotalRefundAmount": str(return_model.refund_amount),
                                         "notifierTotalRefundCurrency": "EUR",
                                         "refundLineItems": [{"eBayItemId": ebay_order_click_and_collect_line_item.orderable_item.ebay_item_id,
                                                              "eBayTransactionId": ebay_order_click_and_collect_line_item.transaction_id,
                                                              "notifierRefundAmount": str(return_item.refund_amount),
                                                              "notifierRefundCurrency": "EUR",
                                                              "notifierRefundQuantity": return_item.refund_quantity}]})

        # assert post condition after ebay sync
        self.assertPostcondition(return_model.synced_with_ebay, True)

    def _create_order_with_immediate_core_return(self, product, is_click_and_collect):
        """
        :type product: inventorum_ebay.apps.products.models.EbayProductModel
        :type is_click_and_collect: bool

        :rtype: (inventorum_ebay.apps.orders.models.OrderModel, int)
        :returns: order model instance and core return id
        """
        order_extra = {}
        if is_click_and_collect:
            order_extra["selected_shipping__service"] = self.get_shipping_service_click_and_collect()

        order = OrderModelFactory.create(account=self.account, **order_extra)
        order_line_item = OrderLineItemModelFactory.create(order=order,
                                                           orderable_item__product=product,
                                                           orderable_item__account=self.account,
                                                           quantity=5)

        core_order_creation_data = OrderModelCoreAPIDataSerializer(order).data
        # create closed ebay order to be able to make returns
        core_order_creation_data["state"] |= BinaryCoreOrderStates.CLOSED
        core_order = self.account.core_api.create_order(data=core_order_creation_data)
        core_order_line_item = core_order.basket.items[0]

        order.inv_id = core_order.id
        order.save()

        order_line_item.inv_id = core_order_line_item.id
        order_line_item.save()

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
        core_api = "inventorum_ebay.apps.accounts.models.EbayAccountModel.core_api"
        self.core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))

        core_return_syncer = "inventorum_ebay.apps.returns.core_returns_sync.CoreReturnSyncer.__call__"
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
        self.schedule_ebay_return_event_mock = \
            self.patch("inventorum_ebay.apps.returns.core_returns_sync.schedule_ebay_return_event")

    def reset_mocks(self):
        self.schedule_ebay_return_event_mock.reset_mock()

    def create_order(self, ebay_item, quantity, is_click_and_collect):
        """
        :type ebay_item: inventorum_ebay.apps.products.models.EbayItemModel
        :type quantity: int
        :type is_click_and_collect: bool

        :rtype: inventorum_ebay.apps.orders.models.OrderModel
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
        :type order: inventorum_ebay.apps.orders.models.OrderModel
        :type quantity: int

        :rtype: inventorum_ebay.lib.core_api.models.CoreDeltaReturn
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

        returns = ReturnModel.objects.all()
        self.assertPrecondition(returns.count(), 0)

        core_return = self.create_core_return(order, quantity=3)

        self.sync(core_return, order)

        self.assertPostcondition(returns.count(), 1)

        return_model = returns.last()

        self.assertEqual(return_model.order, order)
        self.assertEqual(return_model.inv_id, core_return.id)
        self.assertEqual(return_model.refund_type, EbayRefundType.EBAY)
        self.assertEqual(return_model.refund_amount, core_return.total_amount)

        return_item = return_model.items.first()
        core_return_item = core_return.items[0]

        self.assertEqual(return_item.order_line_item, order.line_items.first())
        self.assertEqual(return_item.inv_id, core_return_item.id)
        self.assertEqual(return_item.refund_amount, core_return_item.amount)
        self.assertEqual(return_item.refund_quantity, core_return_item.quantity)

        self.assertTrue(self.schedule_ebay_return_event_mock.called)
        self.schedule_ebay_return_event_mock\
            .assert_called_once_with(return_id=return_model.id, context=self.sync.get_task_execution_context())

        # assert that returns are not handled twice
        self.reset_mocks()

        self.sync(core_return, order)

        self.assertPostcondition(returns.count(), 1)
        self.assertFalse(self.schedule_ebay_return_event_mock.called)

    def test_does_not_handle_non_click_and_collect_returns(self):
        ebay_item = EbayItemFactory()
        order = self.create_order(ebay_item, quantity=1, is_click_and_collect=False)

        returns = ReturnModel.objects.all()
        self.assertPrecondition(returns.count(), 0)

        core_return = self.create_core_return(order, quantity=1)

        self.sync(core_return, order)

        self.assertPostcondition(returns.count(), 0)
        self.assertFalse(self.schedule_ebay_return_event_mock.called)
