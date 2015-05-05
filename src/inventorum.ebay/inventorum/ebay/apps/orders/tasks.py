# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime
from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.orders.services import CoreOrderService

from inventorum.util.celery import inventorum_task
from requests.exceptions import RequestException


log = logging.getLogger(__name__)


@inventorum_task()
def periodic_ebay_orders_sync_task(self):
    from inventorum.ebay.apps.orders.ebay_orders_sync import PeriodicEbayOrdersSync

    start_time = datetime.now()

    accounts = EbayAccountModel.objects.ebay_authenticated().all()
    log.info("Starting ebay order sync for {} accounts".format(accounts.count()))

    for account in accounts:
        log.info("Running ebay order sync for account {}".format(account))
        PeriodicEbayOrdersSync(account).run()

    run_time = datetime.now() - start_time
    log.info("Finished ebay order sync in {}".format(run_time))


@inventorum_task(max_retries=5, default_retry_delay=30)
def core_order_creation_task(self, order_id):
    """
    :type order_id: int
    """
    account = EbayAccountModel.objects.get(id=self.context.account_id)
    order = OrderModel.objects.get(id=order_id)

    service = CoreOrderService(account)

    try:
        service.create_in_core_api(order)
    except RequestException as e:
        log.error(e)
        # TODO jm: Overwrite retry to pass context automatically
        self.retry(kwargs=dict(context=self.context))


def schedule_core_order_creation(order_id, context):
    """
    :type order_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    core_order_creation_task.delay(order_id, context=context)


@inventorum_task()
def send_click_and_collect_event_task(self, order_id, event_type):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type order_id: int
    :type event_type: unicode
    """
    pass


def schedule_click_and_collect_event(order_id, event_type, context):
    """
    :type order_id: int
    :type event_type: unicode
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    send_click_and_collect_event_task.delay(order_id, event_type, context=context)


@inventorum_task()
def ebay_order_status_update_task(self, order_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type order_id: int
    """
    pass


def schedule_ebay_order_status_update(order_id, context):
    """
    :type order_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    ebay_order_status_update_task.delay(order_id, context=context)
