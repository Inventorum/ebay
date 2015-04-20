# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.products.models import EbayItemUpdateModel, EbayItemModel, EbayProductModel
from inventorum.ebay.apps.products.services import UpdateService, UnpublishingService, ProductDeletionService
from inventorum.util.celery import inventorum_task, TaskExecutionContext


log = logging.getLogger(__name__)


@inventorum_task()
def ebay_item_unpublishing_task(self, ebay_item_id):
    ebay_item = EbayItemModel.objects.get(ebay_item_id)
    service = UnpublishingService(ebay_item.product, self.account.default_user)
    service.unpublish()


def schedule_ebay_item_unpublishing(ebay_item):
    log.info("Scheduled ebay item unpublishing: {}".format(ebay_item))
    ebay_item_unpublishing_task.delay(ebay_item.id)


@inventorum_task()
def ebay_item_update_task(self, ebay_item_update_id):
    ebay_item_update = EbayItemUpdateModel.objects.get(ebay_item_update_id)
    service = UpdateService(self.account.default_user, ebay_item_update)
    service.update()


def schedule_ebay_item_update(ebay_item_update):
    log.info("Scheduled ebay item update: {}".format(ebay_item_update))
    # ebay_item_update_task.delay(ebay_item_update.id,
    #                             context=TaskExecutionContext(user_id=1, account_id=1, request_id=None))


@inventorum_task()
def ebay_product_deletion_task(self, ebay_product_id):
    ebay_product = EbayProductModel.objects.get(ebay_product_id)
    service = ProductDeletionService(self.account.default_user, ebay_product)
    service.delete()


def schedule_ebay_product_deletion(ebay_product):
    log.info("Scheduled ebay item deletion: {}".format(ebay_product))
    # ebay_product_deletion_task.delay(ebay_product.id, )
