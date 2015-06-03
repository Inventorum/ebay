# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from celery.utils.log import get_task_logger
from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.returns.models import ReturnModel
from inventorum.ebay.apps.returns.services import EbayReturnService
from inventorum.util.celery import inventorum_task


log = get_task_logger(__name__)


@inventorum_task()
def periodic_core_returns_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    accounts = EbayAccountModel.objects.ebay_authenticated().all()
    log.info("Triggering periodic core returns sync for {} accounts".format(accounts.count()))

    for account in accounts:
        core_returns_sync_task.delay(account.id, context=self.context)


@inventorum_task()
def core_returns_sync_task(self, account_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    from inventorum.ebay.apps.returns.core_returns_sync import CoreReturnsSync
    start_time = datetime.now()

    account = EbayAccountModel.objects.get(pk=account_id)
    log.info("Starting core returns sync for %s", account)

    CoreReturnsSync(account).run()

    run_time = datetime.now() - start_time
    log.info("Finished core returns sync for %s in %s", account, run_time)


@inventorum_task()
def ebay_return_event_task(self, return_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    account = EbayAccountModel.objects.get(id=self.context.account_id)
    return_model = ReturnModel.objects.get(id=return_id)

    service = EbayReturnService(account, return_model)
    service.send_ebay_return_event()


def schedule_ebay_return_event(return_id, context):
    """
    :type return_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    ebay_return_event_task.delay(return_id, context=context)
