# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime

from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.products.core_products_sync import CoreProductsSync


log = logging.getLogger(__name__)


def run(*args):
    start_time = datetime.now()

    accounts = EbayAccountModel.objects.with_published_products().all()
    log.info("Starting core api sync for {} accounts".format(accounts.count()))

    for account in accounts:
        log.info("Running core api sync for inv account {}".format(account.inv_id))
        CoreProductsSync(account).run()

    run_time = datetime.now() - start_time
    log.info("Finished core api sync in {}".format(run_time))
