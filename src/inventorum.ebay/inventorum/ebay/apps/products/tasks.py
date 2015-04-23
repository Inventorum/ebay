# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.accounts.models import EbayUserModel
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemUpdateModel, EbayProductModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingSendStateFailedException,\
    PublishingException, UnpublishingService, UnpublishingException, UpdateService, UpdateFailedException, \
    ProductDeletionService

from inventorum.util.celery import inventorum_task


log = logging.getLogger(__name__)


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

    :rtype: celery.result.AsyncResult
    """
    initialize_unpublish = _initialize_ebay_item_unpublish.si(ebay_item_id, context=context)
    unpublish = _ebay_item_unpublish.si(ebay_item_id, context=context)
    finalize_unpublish = _finalize_ebay_item_unpublish.si(ebay_item_id, context=context)

    return (initialize_unpublish | unpublish | finalize_unpublish)()


# - Update tasks --------------------------------------------------------

@inventorum_task()
def ebay_item_update(self, ebay_item_update_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_update_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    item_update = EbayItemUpdateModel.objects.get(id=ebay_item_update_id)

    service = UpdateService(item_update, user=user)

    try:
        service.update()
    except UpdateFailedException as e:
        log.error("Update failed with ebay errors: %s", e.original_exception.errors)


def schedule_ebay_item_update(ebay_item_update_id, context):
    """
    :type ebay_item_update_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    ebay_item_update.delay(ebay_item_update_id, context=context)


@inventorum_task()
def ebay_product_deletion(self, ebay_product_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_product_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    product = EbayProductModel.objects.get(pk=ebay_product_id, account_id=self.context.account_id)

    service = ProductDeletionService(product, user=user)
    # may raise UnpublishingException in case required unpublishing failed -> this task fails as well, which is intended
    service.delete()


def schedule_ebay_product_deletion(ebay_product_id, context):
    """
    :type ebay_product_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    ebay_product_deletion.delay(ebay_product_id, context=context)
