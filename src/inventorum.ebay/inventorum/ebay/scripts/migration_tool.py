# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import plac
from inventorum.util.paste import boostrap_from_config

log = logging.getLogger(__name__)


@plac.annotations(
    config_file=plac.Annotation("paster config file", 'positional', None, str),
    inv_account_id=plac.Annotation("inv account id", 'positional', None, int)
)
def _migrate_from_old_ebay(config_file, inv_account_id):
    boostrap_from_config(config_file)

    from inventorum.ebay.apps.items.ebay_items_sync_services import EbayItemsSync
    from inventorum.ebay.apps.accounts.models import EbayAccountModel

    account = EbayAccountModel.objects.get(inv_id=inv_account_id)
    log.info('Start syncing items for %s', inv_account_id)
    EbayItemsSync(account).run()


def migrate_from_old_ebay():
    plac.call(_migrate_from_old_ebay)
