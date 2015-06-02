# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime
from django.db import transaction
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.returns import EbayRefundType
from inventorum.ebay.apps.returns.models import ReturnModel
from inventorum.ebay.apps.returns.tasks import schedule_ebay_return_event
from inventorum.util.celery import TaskExecutionContext


log = logging.getLogger(__name__)


class CoreReturnsSync(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        self.sync = CoreReturnSyncer(account=self.account)

    def run(self):
        """
        Invokes the ``CoreReturnSyncer`` for every core return that was created or modified since the last sync date.
        In case it is the first sync, the ebay account creation is taken as starting point for the synchronization.
        """
        current_sync_start = datetime.utcnow()
        
        # if there was no sync yet, the ebay account creation is taken as starting point
        last_sync_start = self.account.last_core_returns_sync or self.account.time_added

        core_returns_with_matching_orders = \
            self._get_core_returns_with_matching_orders(return_created_or_updated_since=last_sync_start)

        for core_return, order in core_returns_with_matching_orders:
            self.sync(core_return, order)

        self.account.last_core_returns_sync = current_sync_start
        self.account.save()

    def _get_core_returns_with_matching_orders(self, return_created_or_updated_since):
        pages = self.account.core_api.returns.get_paginated_delta(start_date=return_created_or_updated_since)
        for page in pages:
            for core_return in page:
                try:
                    ebay_order = OrderModel.objects.by_account(self.account).by_inv_id(core_return.order_id).get()
                    yield core_return, ebay_order
                except OrderModel.DoesNotExist:
                    log.error("Could not find matching order for delta return with `order.inv_id={}`"
                              .format(core_return.order_id))


class CoreReturnSyncer(object):

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

    @transaction.atomic()
    def __call__(self, core_return, order):
        """
        :type core_return: inventorum.ebay.lib.core_api.models.CoreDeltaReturn
        :type order: inventorum.ebay.apps.orders.models.OrderModel
        """
        # For now, only click & collect orders can be returned through ebay
        if not order.is_click_and_collect:
            log.info("Return with `inv_id=%s` for non-click-and-collect order %s skipped", core_return.id, order)
            return

        if ReturnModel.objects.by_inv_id(core_return.id).exists():
            log.info("Return with `inv_id=%s` for order %s already synced", core_return.id, order)
            return

        # Since we do not support combined ebay orders yet, we rely on exactly one order line item...
        if order.line_items.count() > 1:
            log.error("Return with `inv_id=%s` skipped because order %s has more than one line item",
                      core_return.id, order)
            return

        # ...and one matching return item
        if len(core_return.items) > 1:
            log.error("Return with `inv_id=%s` for order %s skipped as it has more than one return item.",
                      core_return.id, order)
            return

        core_return_item, order_line_item = core_return.items[0], order.line_items.first()

        return_model = ReturnModel.objects.create(inv_id=core_return.id,
                                                  order=order,
                                                  refund_type=EbayRefundType.EBAY,
                                                  refund_amount=core_return.total_amount)

        return_model.items.create(inv_id=core_return_item.id,
                                  order_line_item=order_line_item,
                                  refund_quantity=core_return_item.quantity,
                                  refund_amount=core_return_item.amount)

        schedule_ebay_return_event(return_id=return_model.id, context=self.get_task_execution_context())

        log.info("Handled return with `inv_id=%s` for click-and-collect order %s", core_return.id, order)
