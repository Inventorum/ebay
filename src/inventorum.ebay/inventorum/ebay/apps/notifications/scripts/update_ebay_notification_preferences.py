# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.lib.ebay.authentication import EbayAuthentication


log = logging.getLogger(__name__)


def run(*args):
    accounts = EbayAccountModel.objects.exclude(token=None)

    for acc in accounts:
        log.info('Updating acc[%s] with %s', acc, acc.token.value)
        token = acc.token.ebay_object
        auth_api = EbayAuthentication(token=token)
        try:
            auth_api.update_notification_settings()
        except Exception:
            pass

