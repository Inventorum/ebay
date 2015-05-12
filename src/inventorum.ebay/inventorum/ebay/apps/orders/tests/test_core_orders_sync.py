# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime, timedelta

from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory
from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.lib.core_api.models import CoreOrder
from inventorum.ebay.lib.core_api.tests.factories import CoreOrderFactory
from inventorum.ebay.apps.orders.core_orders_sync import CoreOrdersSync, CoreOrderSyncer
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.orders.tasks import periodic_core_orders_sync_task
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context
from inventorum.ebay.lib.ebay.data.events import EbayEventType
from inventorum.ebay.tests.testcases import UnitTestCase, EbayAuthenticatedAPITestCase
from inventorum.util.celery import TaskExecutionContext
from mock import PropertyMock


log = logging.getLogger(__name__)


class IntegrationTestPeriodicCoreOrdersSync(EbayAuthenticatedAPITestCase):

    @celery_test_case()
    def smoke_test(self):
        core_api_mock = self.patch("inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api",
                                   new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))

        ebay_events_publish_mock = self.patch("inventorum.ebay.lib.ebay.events.EbayInboundEvents.publish")
        ebay_orders_complete_sale_mock = self.patch("inventorum.ebay.lib.ebay.orders.EbayOrders.complete_sale")

        order = OrderModelFactory.create(account=self.account,
                                         inv_id=5000)
        click_and_collect_service = ShippingServiceModel.get_click_and_collect_service(self.account.country)
        click_and_collect_order = OrderModelFactory.create(account=self.account,
                                                           inv_id=5001,
                                                           selected_shipping__service=click_and_collect_service)
        self.assertPrecondition(click_and_collect_order.is_click_and_collect, True)

        core_order = CoreOrderFactory(id=order.inv_id,
                                      state=BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED)

        click_and_collect_core_order = CoreOrderFactory(id=click_and_collect_order.inv_id,
                                                        state=BinaryCoreOrderStates.SHIPPED | BinaryCoreOrderStates.CLOSED)

        core_api_mock.get_paginated_orders_delta.return_value = iter([[core_order, click_and_collect_core_order]])

        periodic_core_orders_sync_task.delay(context=get_anonymous_task_execution_context())

        self.assertTrue(core_api_mock.get_paginated_orders_delta.called)

        self.assertEqual(ebay_events_publish_mock.call_count, 2)
        self.assertEqual(ebay_orders_complete_sale_mock.call_count, 1)


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
        order_1 = OrderModelFactory.create(inv_id=20002)
        core_order_1 = CoreOrderFactory.create(id=order_1.inv_id, state=BinaryCoreOrderStates.PENDING)

        order_2 = OrderModelFactory.create(inv_id=20003)
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


class UnitTestCoreOrderSyncer(UnitTestCase):

    def setUp(self):
        super(UnitTestCoreOrderSyncer, self).setUp()

        self.account = EbayAccountFactory.create()
        self.default_user = EbayUserFactory.create(account=self.account)

        # syncer is state-less, no need to regenerate it
        self.sync = CoreOrderSyncer(account=self.account)

        self.setup_mocks()

    def setup_mocks(self):
        self.schedule_ebay_order_status_update_mock = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_ebay_order_status_update")

        self.schedule_click_and_collect_status_update_with_event = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_click_and_collect_status_update_with_event")

    def reset_mocks(self):
        self.schedule_click_and_collect_status_update_with_event.reset_mock()
        self.schedule_ebay_order_status_update_mock.reset_mock()

    def _get_fresh_order(self, **factory_kwargs):
        """
        :rtype: OrderModel
        """
        factory_params = dict(inv_id=1337,
                              core_status__is_paid=False,
                              core_status__is_shipped=False,
                              core_status__is_closed=False,
                              core_status__is_canceled=False)

        factory_params.update(factory_kwargs)
        return OrderModelFactory.create(**factory_params)

    def _get_fresh_click_and_collect_order(self, **factory_kwargs):
        """
        :rtype: OrderModel
        """
        order = self._get_fresh_order(**factory_kwargs)

        order.selected_shipping.service = ShippingServiceModel.get_click_and_collect_service(order.account.country)
        order.selected_shipping.save()
        self.assertPrecondition(order.is_click_and_collect, True)

        return order

    def _get_core_order_for(self, order, with_state):
        """
        :type order: OrderModel
        :type with_state: int

        :rtype: CoreOrder
        """
        return CoreOrderFactory(id=order.id,
                                state=with_state)

    def test_task_execution_context(self):
        self.assertEqual(self.sync.get_task_execution_context(),
                         TaskExecutionContext(user_id=self.default_user.id, account_id=self.account.id,
                                              request_id=None))

    def test_without_changes(self):
        order = self._get_fresh_order()
        core_order = self._get_core_order_for(order, with_state=BinaryCoreOrderStates.PENDING)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     False)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_without_changes_with_click_and_collect(self):
        order = self._get_fresh_click_and_collect_order()
        core_order = self._get_core_order_for(order, with_state=BinaryCoreOrderStates.PENDING)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     False)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_core_status_is_paid_changes(self):
        # set is_paid to True ###############################
        order = self._get_fresh_order()
        core_state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertTrue(self.schedule_ebay_order_status_update_mock.called)
        self.schedule_ebay_order_status_update_mock.assert_called_with(order_id=order.id,
                                                                       context=self.sync.get_task_execution_context())
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # sync again with the same state ####################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_paid back to False #########################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PENDING

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     False)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertTrue(self.schedule_ebay_order_status_update_mock.called)
        self.schedule_ebay_order_status_update_mock.assert_called_with(order_id=order.id,
                                                                       context=self.sync.get_task_execution_context())
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_core_status_is_paid_changes_with_click_and_collect(self):
        # set is_paid to True ###############################
        order = self._get_fresh_click_and_collect_order()
        core_state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        # apart from the state change, there shouldn't be any side effects here for click and collect orders
        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_paid back to False #########################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PENDING

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     False)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_core_status_is_shipped_changes(self):
        # set is_shipped to True ############################
        order = self._get_fresh_order()
        # we also set is_paid to true to test two combined status updates
        core_state = BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  True)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertTrue(self.schedule_ebay_order_status_update_mock.called)
        # although is_paid and is_shipped changed, there should only be one schedule order status update
        self.schedule_ebay_order_status_update_mock.assert_called_once_with(order_id=order.id,
                                                                            context=self.sync.get_task_execution_context())
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # sync again with the same state ####################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_shipped back to False #######################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PAID

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertTrue(self.schedule_ebay_order_status_update_mock.called)
        self.schedule_ebay_order_status_update_mock.assert_called_with(order_id=order.id,
                                                                       context=self.sync.get_task_execution_context())
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_core_status_is_shipped_changes_with_click_and_collect(self):
        # set is_shipped to True ###############################
        order = self._get_fresh_click_and_collect_order()
        core_state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  True)
        self.assertEqual(order.core_status.is_ready_for_pickup, True)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertTrue(self.schedule_click_and_collect_status_update_with_event.called)
        self.schedule_click_and_collect_status_update_with_event.assert_called_once_with(
            order_id=order.id,
            event_type=EbayEventType.READY_FOR_PICKUP,
            context=self.sync.get_task_execution_context())

        # sync again with the same state ####################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_shipped back to False #########################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_ready_for_pickup, False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

    def test_core_status_is_closed_changes(self):
        # set is_closed to True ############################
        order = self._get_fresh_order(core_status__is_paid=True, core_status__is_shipped=True)
        core_state = BinaryCoreOrderStates.CLOSED | BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  True)
        self.assertEqual(order.core_status.is_closed,   True)
        self.assertEqual(order.core_status.is_canceled, False)

        # apart from the state change, there shouldn't be any side effects here if it's not click-and-collect
        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # sync again with the same state ####################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_closed back to False #######################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  True)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        # apart from the state change, there shouldn't be any side effects here if it's not click-and-collect
        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_core_status_is_closed_changes_with_click_and_collect(self):
        # set is_closed to True ###############################
        order = self._get_fresh_click_and_collect_order(core_status__is_paid=True, core_status__is_shipped=True)
        core_state = BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED | BinaryCoreOrderStates.CLOSED
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  True)
        self.assertEqual(order.core_status.is_closed,   True)
        self.assertEqual(order.core_status.is_picked_up, True)
        self.assertEqual(order.core_status.is_canceled, False)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertTrue(self.schedule_click_and_collect_status_update_with_event.called)
        self.schedule_click_and_collect_status_update_with_event.assert_called_once_with(
            order_id=order.id,
            event_type=EbayEventType.PICKED_UP,
            context=self.sync.get_task_execution_context())

        # sync again with the same state ####################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_closed back to False #########################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.SHIPPED

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  True)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_picked_up, False)
        self.assertEqual(order.core_status.is_canceled, False)

    def test_core_status_is_canceled_changes(self):
        # set is_canceled to True ############################
        order = self._get_fresh_order(core_status__is_paid=True)
        core_state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.CANCELED
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, True)

        # apart from the state change, there shouldn't be any side effects here if it's not click-and-collect
        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # sync again with the same state ######################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_canceled back to False #######################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)

        # apart from the state change, there shouldn't be any side effects here if it's not click-and-collect
        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

    def test_core_status_is_canceled_changes_with_click_and_collect(self):
        # set is_canceled to True ###############################
        order = self._get_fresh_click_and_collect_order(core_status__is_paid=True, core_status__is_shipped=True)
        core_state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID | BinaryCoreOrderStates.CANCELED
        core_order = self._get_core_order_for(order, with_state=core_state)

        self.sync(order, core_order)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, True)
        self.assertEqual(order.core_status.is_pickup_canceled, True)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertTrue(self.schedule_click_and_collect_status_update_with_event.called)
        self.schedule_click_and_collect_status_update_with_event.assert_called_once_with(
            order_id=order.id,
            event_type=EbayEventType.CANCELED,
            context=self.sync.get_task_execution_context())

        # sync again with the same state ########################
        self.reset_mocks()

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        # set is_canceled back to False #########################
        self.reset_mocks()
        core_order.state = BinaryCoreOrderStates.PENDING | BinaryCoreOrderStates.PAID

        self.sync(order, core_order)

        self.assertFalse(self.schedule_ebay_order_status_update_mock.called)
        self.assertFalse(self.schedule_click_and_collect_status_update_with_event.called)

        order = order.reload()
        self.assertEqual(order.core_status.is_paid,     True)
        self.assertEqual(order.core_status.is_shipped,  False)
        self.assertEqual(order.core_status.is_closed,   False)
        self.assertEqual(order.core_status.is_canceled, False)
        self.assertEqual(order.core_status.is_pickup_canceled, False)
