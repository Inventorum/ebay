# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime
from inventorum.ebay.apps.orders import tasks
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.lib.ebay.data.events import EbayEventType
from inventorum.util.celery import TaskExecutionContext


log = logging.getLogger(__name__)


class CoreOrdersSync(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        self.sync = CoreOrderSyncer(account=self.account)

    def run(self):
        current_sync_start = datetime.utcnow()
        # if there was no sync yet, the ebay account creation is taken as starting point
        last_sync_start = self.account.last_core_orders_sync or self.account.time_added

        modified_ebay_orders = self._get_modified_ebay_orders(modified_since=last_sync_start)
        for order, core_order in modified_ebay_orders:
            self.sync(order, core_order)

        self.account.last_core_orders_sync = current_sync_start
        self.account.save()

    def _get_modified_ebay_orders(self, modified_since):
        """
        :type modified_since:
        :rtype: collections.Iterable[(inventorum.ebay.apps.orders.models.OrderModel, inventorum.ebay.apps.core_api.models.CoreOrder)]
        """
        pages = self.account.core_api.get_paginated_orders_delta(start_date=modified_since)
        for page in pages:
            for core_order in page:
                try:
                    ebay_order = OrderModel.objects.by_inv_id(core_order.id).get()
                    yield ebay_order, core_order
                except OrderModel.DoesNotExist:
                    log.error("Could not find matching order for delta order with `inv_id={}`".format(core_order.id))


class CoreOrderSyncer(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def get_task_execution_context(self):
        """
        :rtype: inventorum.util.celery.TaskExecutionContext
        """
        return TaskExecutionContext(user_id=self.account.default_user.id,
                                    account_id=self.account.id,
                                    request_id=None)

    def __call__(self, order, core_order):
        """
        :type order: OrderModel
        :type core_order: inventorum.ebay.apps.core_api.models.CoreOrder
        """
        # Since multiple non click-and-collect status updates can be performed with one call, we do it once in the end
        regular_ebay_status_update_required = False

        if order.core_status.is_paid != core_order.is_paid:
            order.core_status.is_paid = core_order.is_paid
            order.core_status.save()

            regular_ebay_status_update_required = not order.is_click_and_collect

        if order.core_status.is_shipped != core_order.is_shipped:
            order.core_status.is_shipped = core_order.is_shipped
            order.core_status.save()

            regular_ebay_status_update_required = not order.is_click_and_collect
            # if is_shipped was set to true for click and collect orders => send appropriate event
            # note: for now, the event will always be send again if the core state was flipped multiple times
            if order.is_click_and_collect and order.core_status.is_ready_for_pickup:
                tasks.schedule_click_and_collect_status_update_with_event(order_id=order.id,
                                                                          event_type=EbayEventType.READY_FOR_PICKUP,
                                                                          context=self.get_task_execution_context())

        if order.core_status.is_delivered != core_order.is_delivered:
            order.core_status.is_delivered = core_order.is_delivered
            order.core_status.save()

            # if it's a regular, non click-and-collect order, nothing needs to be done here
            # note: for now, the event will always be send again if the core state was flipped multiple times
            if order.is_click_and_collect and order.core_status.is_picked_up:
                tasks.schedule_click_and_collect_status_update_with_event(order_id=order.id,
                                                                          event_type=EbayEventType.PICKED_UP,
                                                                          context=self.get_task_execution_context())

        if order.core_status.is_canceled != core_order.is_canceled:
            order.core_status.is_canceled = core_order.is_canceled
            order.core_status.save()

            if order.is_click_and_collect and order.core_status.is_pickup_canceled:
                tasks.schedule_click_and_collect_status_update_with_event(order_id=order.id,
                                                                          event_type=EbayEventType.CANCELED,
                                                                          context=self.get_task_execution_context())
            elif not order.is_click_and_collect and order.core_status.is_canceled:
                log.error("Non-click-and-collect order {} was canceled in core api but regular ebay orders "
                          "cannot be canceled right now.".format(order))

        if regular_ebay_status_update_required:
            tasks.schedule_ebay_order_status_update(order_id=order.id, context=self.get_task_execution_context())

        if order.core_status.is_closed != core_order.is_closed:
            order.core_status.is_closed = core_order.is_closed
            order.core_status.save()
