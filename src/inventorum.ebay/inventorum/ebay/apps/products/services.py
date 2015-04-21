# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from decimal import Decimal

from django.utils.functional import cached_property
from django.utils.translation import ugettext
from requests.exceptions import HTTPError

from inventorum.ebay.apps.products import EbayItemPublishingStatus, EbayApiAttemptType
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod, EbayItemSpecificModel, EbayApiAttempt
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


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


class PublishingUnpublishingService(object):

    def __init__(self, product, user):
        """
        Service for publishing products to ebay
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

    def validate(self):
        """
        Validates account and product before publishing to ebay
        :raises: PublishingValidationException
        """
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

        if self.product.is_published:
            raise PublishingValidationException(ugettext('Product was already published'))

        specific_values_ids = set(sv.specific.pk for sv in self.product.specific_values.all())
        required_ones = set(self.product.category.specifics.required().values_list('id', flat=True))

        missing_ids = (required_ones - specific_values_ids)
        if missing_ids:
            raise PublishingValidationException(
                ugettext('You need to pass all required specifics (missing: %(missing_ids)s)!')
                % {'missing_ids': list(missing_ids)})

    def prepare(self):
        """
        Create all necessary models for later publishing in async task
        :return:
        """
        item = self._create_db_item()
        return item

    def _create_db_item(self):

        db_product = EbayProductModel.objects.get(inv_id=self.core_product.id)

        item = EbayItemModel.objects.create(
            listing_duration=db_product.category.features.max_listing_duration,
            product=db_product,
            account=db_product.account,
            name=self.core_product.name,
            description=self.core_product.description,
            gross_price=self.core_product.gross_price,
            category=db_product.category,
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

        for specific in db_product.specific_values.all():
            EbayItemSpecificModel.objects.create(
                specific=specific.specific,
                value=specific.value,
                item=item
            )

        return item

    def initialize_publish_attempt(self, item):
        """
        :type item: EbayItemModel

        :raises PublishingSendStateFailedException
        """
        # TODO jm: PUBLISH_IN_PROGRESS?
        item.set_publishing_status(EbayItemPublishingStatus.IN_PROGRESS)
        self.send_publishing_status_to_core_api(item.publishing_status)

    def publish(self, item):
        """
        :type item: EbayItemModel

        :raises PublishingException
        """
        ebay_api = EbayItems(self.user.account.token.ebay_object)
        try:
            response = ebay_api.publish(item.ebay_object)
        except EbayConnectionException as e:
            # TODO jm: PUBLISH_FAILED?
            item.set_publishing_status(EbayItemPublishingStatus.FAILED, details=[err.api_dict() for err in e.errors])

            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=item,
                type=EbayApiAttemptType.PUBLISH
            )

            raise PublishingException(e.message, original_exception=e)

        item.external_id = response.item_id
        item.published_at = response.start_time
        item.ends_at = response.end_time
        item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, save=False)
        item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=ebay_api,
            item=item,
            type=EbayApiAttemptType.PUBLISH
        )

    def finalize_publish_attempt(self, item):
        """
        :type item: EbayItemModel

        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(item.publishing_status, details=item.publishing_status_details)


class UnpublishingService(PublishingUnpublishingService):

    def validate(self):
        if not self.product.is_published:
            raise PublishingValidationException(ugettext('Product is not published'))

    def get_item(self):
        return self.product.published_item

    def initialize_unpublish_attempt(self, item):
        """
        :type item: EbayItemModel

        :raises PublishingSendStateFailedException
        """
        # TODO jm: UNPUBLISH_IN_PROGRESS?
        item.set_publishing_status(EbayItemPublishingStatus.IN_PROGRESS)
        self.send_publishing_status_to_core_api(item.publishing_status)

    def unpublish(self, item):
        """
        :type item: EbayItemModel

        :raises UnpublishingException
        """
        service = EbayItems(self.user.account.token.ebay_object)
        try:
            response = service.unpublish(item.external_id)
        except EbayConnectionException as e:
            # TODO jm: UNPUBLISH_FAILED?
            item.set_publishing_status(EbayItemPublishingStatus.PUBLISHED, details=[err.api_dict() for err in e.errors])

            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=item,
                type=EbayApiAttemptType.UNPUBLISH
            )

            raise UnpublishingException(e.message, original_exception=e)

        item.unpublished_at = response.end_time
        item.set_publishing_status(EbayItemPublishingStatus.UNPUBLISHED, save=False)
        item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=service,
            item=item,
            type=EbayApiAttemptType.UNPUBLISH
        )

    def finalize_unpublish_attempt(self, item):
        """
        :type item: EbayItemModel

        :raises: PublishingSendStateFailedException
        """
        self.send_publishing_status_to_core_api(item.publishing_status, details=item.publishing_status_details)
