# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.accounts.models import EbayUserModel
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemUpdateModel, EbayProductModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingSendStateFailedException,\
    PublishingException, UnpublishingService, UnpublishingException

from inventorum.util.celery import inventorum_task


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
    # service = UpdateService(self.account.default_user, ebay_item_update)
    # service.update()


def schedule_ebay_item_update(ebay_item_update):
    log.info("Scheduled ebay item update: {}".format(ebay_item_update))
    # ebay_item_update_task.delay(ebay_item_update.id,
    #                             context=TaskExecutionContext(user_id=1, account_id=1, request_id=None))


@inventorum_task()
def ebay_product_deletion_task(self, ebay_product_id):
    ebay_product = EbayProductModel.objects.get(ebay_product_id)
    # service = ProductDeletionService(self.account.default_user, ebay_product)
    # service.delete()


def schedule_ebay_product_deletion(ebay_product):
    log.info("Scheduled ebay item deletion: {}".format(ebay_product))
    # ebay_product_deletion_task.delay(ebay_product.id, )

# - Publishing tasks ----------------------------------------------------

@inventorum_task(max_retries=5, default_retry_delay=30)
def _initialize_ebay_item_publish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = PublishingService(ebay_item, user)

    try:
        service.initialize_publish_attempt()
    except PublishingSendStateFailedException:
        self.retry()


@inventorum_task()
def _ebay_item_publish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = PublishingService(ebay_item, user)

    try:
        service.publish()
    except PublishingException as e:
        log.error("Publishing failed with ebay errors: %s", e.original_exception.errors)
        # no retry, finalize will still be executed to finalize the failed publishing attempt


@inventorum_task(max_retries=5, default_retry_delay=30)
def _finalize_ebay_item_publish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = PublishingService(ebay_item, user)

    try:
        service.finalize_publish_attempt()
    except PublishingSendStateFailedException:
        self.retry()


def schedule_ebay_item_publish(ebay_item_id, context):
    """
    :type ebay_item_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    initialize_publish = _initialize_ebay_item_publish.si(ebay_item_id, context=context)
    publish = _ebay_item_publish.si(ebay_item_id, context=context)
    finalize_publish = _finalize_ebay_item_publish.si(ebay_item_id, context=context)

    (initialize_publish | publish | finalize_publish)()


# - Unpublishing tasks --------------------------------------------------

@inventorum_task(max_retries=5, default_retry_delay=30)
def _initialize_ebay_item_unpublish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = UnpublishingService(ebay_item, user)

    try:
        service.initialize_unpublish_attempt()
    except PublishingSendStateFailedException:
        self.retry()


@inventorum_task()
def _ebay_item_unpublish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = UnpublishingService(ebay_item, user)

    try:
        service.unpublish()
    except UnpublishingException as e:
        log.error("Unpublishing failed with ebay errors: %s", e.original_exception.errors)
        # no retry, finalize will still be executed to finalize the failed unpublishing attempt


@inventorum_task(max_retries=5, default_retry_delay=30)
def _finalize_ebay_item_unpublish(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = UnpublishingService(ebay_item, user)

    try:
        service.finalize_unpublish_attempt()
    except PublishingSendStateFailedException:
        self.retry()


def schedule_ebay_item_unpublish(ebay_item_id, context):
    """
    :type ebay_item_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    initialize_unpublish = _initialize_ebay_item_unpublish.si(ebay_item_id, context=context)
    unpublish = _ebay_item_unpublish.si(ebay_item_id, context=context)
    finalize_unpublish = _finalize_ebay_item_unpublish.si(ebay_item_id, context=context)

    (initialize_unpublish | unpublish | finalize_unpublish)()
