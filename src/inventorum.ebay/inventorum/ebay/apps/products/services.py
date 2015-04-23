# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from decimal import Decimal

from django.utils.functional import cached_property
from django.utils.translation import ugettext
from requests.exceptions import HTTPError

from inventorum.ebay.apps.products import EbayItemPublishingStatus, EbayApiAttemptType, EbayItemUpdateStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod, EbayItemSpecificModel, EbayApiAttempt
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


# TODO jm: Generalize to EbayServiceException?!
class PublishingServiceException(Exception):
    def __init__(self, message=None, original_exception=None):
        self.message = message
        self.original_exception = original_exception


class PublishingException(PublishingServiceException):
    pass


class UnpublishingException(PublishingServiceException):
    pass


class PublishingValidationException(PublishingServiceException):
    pass


class PublishingNotPossibleException(PublishingServiceException):
    pass


class PublishingSendStateFailedException(PublishingServiceException):
    pass


class PublishingCouldNotGetDataFromCoreAPI(PublishingServiceException):
    def __init__(self, response):
        self.response = response


class PublishingPreparationService(object):

    def __init__(self, product, user):
        """
        :type product: EbayProductModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.user = user
        self.product = product

    @cached_property
    def core_product(self):
        try:
            return self.user.core_api.get_product(self.product.inv_id)
        except HTTPError as e:
            raise PublishingCouldNotGetDataFromCoreAPI(response=e.response)

    @cached_property
    def core_info(self):
        try:
            return self.user.core_api.get_account_info()
        except HTTPError as e:
            raise PublishingCouldNotGetDataFromCoreAPI(e.response)

    @property
    def core_account(self):
        return self.core_info.account

    def validate(self):
        """
        Validates account and product before publishing to ebay
        :raises: PublishingValidationException
        """
        if self.product.is_published:
            raise PublishingValidationException(ugettext('Product was already published'))

        if not self.core_account.billing_address:
            raise PublishingValidationException(ugettext('To publish product we need your billing address'))

        if self.core_product.is_parent:
            raise PublishingValidationException(ugettext('Cannot publish products with variations'))

        if not (self.core_product.shipping_services or self.core_account.settings.shipping_services):
            raise PublishingValidationException(ugettext('Product has not shipping services selected'))

        if self.core_product.gross_price < Decimal("1"):
            raise PublishingValidationException(ugettext('Price needs to be greater or equal than 1'))

        if not self.product.category_id:
            raise PublishingValidationException(ugettext('You need to select category'))

        specific_values_ids = set(sv.specific.pk for sv in self.product.specific_values.all())
        required_ones = set(self.product.category.specifics.required().values_list('id', flat=True))

        missing_ids = (required_ones - specific_values_ids)
        if missing_ids:
            raise PublishingValidationException(
                ugettext('You need to pass all required specifics (missing: %(missing_ids)s)!')
                % {'missing_ids': list(missing_ids)})

    def create_ebay_item(self):
        """
        :rtype: EbayItemModel
        """
        product = EbayProductModel.objects.get(inv_id=self.core_product.id)

        item = EbayItemModel.objects.create(
            listing_duration=product.category.features.max_listing_duration,
            product=product,
            account=product.account,
            name=self.core_product.name,
            description=self.core_product.description,
            gross_price=self.core_product.gross_price,
            category=product.category,
            country=self.core_account.country,
            quantity=self.core_product.quantity,
            paypal_email_address=self.core_account.settings.ebay_paypal_email,
            postal_code=self.core_account.billing_address.zipcode
        )

        for image in self.core_product.images:
            EbayItemImageModel.objects.create(
                inv_id=image.id,
                url=image.url,
                item=item
            )
        shipping_services = self.core_product.shipping_services or self.core_account.settings.shipping_services
        for service in shipping_services:
            EbayItemShippingDetails.objects.create(
                additional_cost=service.additional_cost,
                cost=service.cost,
                external_id=service.id,
                item=item
            )

        for payment in self.core_account.settings.ebay_payment_methods:
            EbayItemPaymentMethod.objects.create(
                external_id=payment,
                item=item
            )

        for specific in product.specific_values.all():
            EbayItemSpecificModel.objects.create(
                specific=specific.specific,
                value=specific.value,
                item=item
            )

        return item


class PublishingUnpublishingService(object):

    def __init__(self, item, user):
        """
        Abstract base service for publishing/unpublishing products to ebay
        :type item: EbayItemModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.user = user
        self.item = item

    @property
    def product(self):
        return self.item.product

    def send_publishing_status_to_core_api(self, publishing_status, details=None):
        """
        :param publishing_status: see `EbayItemPublishingStatus`
        :type publishing_status: unicode
        :param details: Additional details, must be json serializable
        """
        core_api_state = EbayItemPublishingStatus.core_api_state(publishing_status)
        if core_api_state is not None:
            try:
                self.user.core_api.post_product_publishing_state(self.product.inv_id, core_api_state, details=details)
            except HTTPError as e:
                log.error(e)
                raise PublishingSendStateFailedException()
        else:
            log.warn('Got state (%s) that cannot be mapped to core api PublishState', publishing_status)


class PublishingService(PublishingUnpublishingService):

    def initialize_publish_attempt(self):
        """
        :raises PublishingSendStateFailedException
        """
        in_progress = EbayItemPublishingStatus.IN_PROGRESS
        self.send_publishing_status_to_core_api(publishing_status=in_progress)
        self.item.set_publishing_status(publishing_status=in_progress)

    def publish(self):
        """
        :raises PublishingException
        """
        ebay_api = EbayItems(self.user.account.token.ebay_object)
        try:
            response = ebay_api.publish(self.item.ebay_object)
        except EbayConnectionException as e:
            self.item.set_publishing_status(EbayItemPublishingStatus.FAILED, details=e.serialized_errors)

            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=self.item,
                type=EbayApiAttemptType.PUBLISH
            )

            raise PublishingException(e.message, original_exception=e)

        self.item.external_id = response.item_id
        self.item.published_at = response.start_time
        self.item.ends_at = response.end_time
        self.item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, save=False)
        self.item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=ebay_api,
            item=self.item,
            type=EbayApiAttemptType.PUBLISH
        )

    def finalize_publish_attempt(self):
        """
        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(self.item.publishing_status,
                                                details=self.item.publishing_status_details)


class UnpublishingService(PublishingUnpublishingService):

    def initialize_unpublish_attempt(self):
        """
        :raises PublishingSendStateFailedException
        """
        in_progress = EbayItemPublishingStatus.IN_PROGRESS
        self.send_publishing_status_to_core_api(publishing_status=in_progress)
        self.item.set_publishing_status(publishing_status=in_progress)

    def unpublish(self):
        """
        :raises UnpublishingException
        """
        service = EbayItems(self.user.account.token.ebay_object)
        try:
            response = service.unpublish(self.item.external_id)
        except EbayConnectionException as e:
            self.item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, details=e.serialized_errors)

            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=self.item,
                type=EbayApiAttemptType.UNPUBLISH
            )

            raise UnpublishingException(e.message, original_exception=e)

        self.item.unpublished_at = response.end_time
        self.item.set_publishing_status(EbayItemPublishingStatus.UNPUBLISHED, save=False)
        self.item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=service,
            item=self.item,
            type=EbayApiAttemptType.UNPUBLISH
        )

    def finalize_unpublish_attempt(self):
        """
        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(self.item.publishing_status,
                                                details=self.item.publishing_status_details)


class UpdateFailedException(PublishingServiceException):
    pass


class UpdateService(object):

    def __init__(self, item_update, user):
        """
        :type item_update: inventorum.ebay.apps.products.models.EbayItemUpdateModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.user = user
        self.item_update = item_update

    def update(self):
        self.item_update.status = EbayItemUpdateStatus.IN_PROGRESS

        ebay_api = EbayItems(self.user.account.token.ebay_object)

        try:
            response = ebay_api.revise_fixed_price_item(self.item_update.ebay_object)
        except EbayConnectionException as e:
            self.item_update.set_status(EbayItemUpdateStatus.FAILED, details=e.serialized_errors)
            EbayApiAttempt.create_failed_update_attempt(self.item_update, exception=e)

            raise UpdateFailedException(e.message, original_exception=e)

        self.item_update.set_status(EbayItemUpdateStatus.SUCCEEDED)
        self._update_ebay_item_model()

        EbayApiAttempt.create_succeeded_update_attempt(item_update=self.item_update, ebay=ebay_api)

    def _update_ebay_item_model(self):
        """ Updates the item model after the update has been acked by ebay """
        ebay_item = self.item_update.item

        if self.item_update.has_updated_quantity:
            ebay_item.quantity = self.item_update.quantity

        if self.item_update.has_updated_gross_price:
            ebay_item.gross_price = self.item_update.gross_price

        ebay_item.save()


class ProductDeletionService(object):

    def __init__(self, product, user):
        """
        :type product: EbayProductModel
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        self.product = product
        self.user = user

    def delete(self):
        """
        :raises UnpublishingException
        :rtype: bool
        """
        if self.product.is_published:

            ebay_item = self.product.published_item

            service = UnpublishingService(ebay_item, self.user)
            service.unpublish()

        self.product.delete()
