# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum_ebay.apps.accounts.models import EbayAccountModel
from inventorum_ebay.lib.ebay.authentication import EbayAuthentication


log = logging.getLogger(__name__)


def run(*args):
    ebay_authenticated_accounts = EbayAccountModel.objects.ebay_authenticated().all()
    for account in ebay_authenticated_accounts:
        ebay_auth = EbayAuthentication(account.token.ebay_object)
        ebay_auth.update_user_preferences()
