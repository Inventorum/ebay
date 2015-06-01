# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from celery.utils.log import get_task_logger
from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.returns.core_returns_sync import CoreReturnsSync
from inventorum.util.celery import inventorum_task


log = get_task_logger(__name__)


@inventorum_task()
def periodic_core_returns_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    start_time = datetime.now()

    accounts = EbayAccountModel.objects.ebay_authenticated().all()
    log.info("Starting core returns sync for {} accounts".format(accounts.count()))

    for account in accounts:
        log.info("Running core returns sync for account {}".format(account))
        CoreReturnsSync(account).run()

    run_time = datetime.now() - start_time
    log.info("Finished core returns sync in {}".format(run_time))
