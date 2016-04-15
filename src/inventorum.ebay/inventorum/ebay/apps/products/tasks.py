# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from celery.utils.log import get_task_logger

from django.utils.translation import ugettext
from inventorum.ebay.apps.accounts.models import EbayUserModel, EbayAccountModel
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemUpdateModel, EbayProductModel, DirtynessRegistry
from inventorum.ebay.apps.products.services import PublishingService, PublishingSendStateFailedException,\
    PublishingException, UnpublishingService, UnpublishingException, UpdateService, UpdateFailedException, \
    ProductDeletionService, CorePublishingStatusUpdateService
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.data.errors import EbayFatalError
from inventorum.ebay.lib.utils import preserve_and_reraise_exception

from inventorum.util.celery import inventorum_task
from requests.exceptions import RequestException


log = get_task_logger(__name__)


@inventorum_task()
def periodic_core_products_sync_task(self):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    from inventorum.ebay.apps.products.core_products_sync import CoreProductsSync

    start_time = datetime.now()

    accounts = EbayAccountModel.objects.with_published_products().all()
    log.info("Starting core products sync for {} accounts".format(accounts.count()))

    for account in accounts:
        log.info("Running core api sync for inv account {}".format(account.inv_id))
        CoreProductsSync(account).run()

    run_time = datetime.now() - start_time
    log.info("Finished core products sync in {}".format(run_time))


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
        self.retry(args=(ebay_item_id,))


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
    except (PublishingException, EbayConnectionException) as e:
        log.error("Publishing failed with ebay errors: %s", e.original_exception.errors)
        # no retry, finalize will still be executed to finalize the failed publishing attempt
    except Exception as e:
        # We fucked up really bad that this happend, so we want to show Exception in celery but still
        # we want to mark product as unpublished
        error = EbayFatalError(self.request.id)
        ebay_item.set_publishing_status(EbayItemPublishingStatus.FAILED, details=[error.api_dict()])
        synchronise_ebay_item_to_api.delay(ebay_item_id, context=self.context)
        preserve_and_reraise_exception()


@inventorum_task(max_retries=5, default_retry_delay=30)
def synchronise_ebay_item_to_api(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    user = EbayUserModel.objects.get(id=self.context.user_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = PublishingService(ebay_item, user)

    try:
        service.finalize_publish_attempt()
        DirtynessRegistry.objects.unregister(ebay_item)
    except PublishingSendStateFailedException:
        self.retry(args=(ebay_item_id,))


def schedule_ebay_item_publish(ebay_item_id, context):
    """
    :type ebay_item_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    publish = _ebay_item_publish.si(ebay_item_id, context=context)
    finalize_publish = synchronise_ebay_item_to_api.si(ebay_item_id, context=context)

    (publish | finalize_publish)()


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
        self.retry(args=(ebay_item_id,))


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
    except Exception as e:
        # We fucked up really bad that this happend, so we want to show Exception in celery but still
        # we want to mark product as unpublished
        error = EbayFatalError(self.request.id)
        ebay_item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, details=[error.api_dict()])
        synchronise_ebay_item_to_api.delay(ebay_item_id, context=self.context)
        preserve_and_reraise_exception()


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
        self.retry(args=(ebay_item_id,))


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


@inventorum_task()
def periodic_ebay_timeouted_item_check_task(self, timeout=300):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    message = ugettext('Publishing timeout (%(timeout)d seconds).') % dict(timeout=timeout)
    details = dict(message=message)

    for item in EbayItemModel.objects.delayed_publishing(timeout):
        item.set_publishing_status(publishing_status=EbayItemPublishingStatus.FAILED,
                                   details=details,
                                   save=True)
        synchronise_ebay_item_to_api.delay(item.id, context=self.context)


@inventorum_task()
def periodic_synchronise_ebay_item_to_api(self, timeout=300):
    """
    :type self: inventorum.util.celery.InventorumTask
    """
    for element in DirtynessRegistry.objects.get_for_model(EbayItemModel).delayed(timeout):
        synchronise_ebay_item_to_api.delay(element.object_id, context=self.context)


# - Publishing state sync -----------------------------------------------

@inventorum_task(max_retries=5, default_retry_delay=30)
def core_api_publishing_status_update_task(self, ebay_item_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type ebay_item_id: int
    """
    account = EbayAccountModel.objects.get(id=self.context.account_id)
    ebay_item = EbayItemModel.objects.get_for_publishing(id=ebay_item_id)

    service = CorePublishingStatusUpdateService(source=ebay_item, account=account)

    try:
        service.update_publishing_status()
    except RequestException as exc:
        log.error(unicode(exc))
        self.retry(args=(ebay_item_id,))


def schedule_core_api_publishing_status_update(ebay_item_id, context):
    """
    :type ebay_item_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    core_api_publishing_status_update_task.delay(ebay_item_id, context=context)
