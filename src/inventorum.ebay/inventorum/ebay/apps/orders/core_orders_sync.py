# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime
from django.utils.functional import cached_property
from inventorum.ebay.apps.products import tasks, EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemUpdateModel, \
    EbayItemVariationModel, EbayItemVariationUpdateModel
from inventorum.util.celery import TaskExecutionContext
from inventorum.util.django.middlewares import fallback_uuid


log = logging.getLogger(__name__)


class CoreOrdersSync(object):

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

    def run(self):
        raise NotImplementedError
