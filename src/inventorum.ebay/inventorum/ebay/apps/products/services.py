# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from decimal import Decimal

from django.utils.functional import cached_property
from django.utils.translation import ugettext
from requests.exceptions import HTTPError

from inventorum.ebay.apps.products import EbayProductPublishingStatus, EbayApiAttemptType
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod, EbayItemSpecificModel, EbayApiAttempt
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


class PublishingServiceException(Exception):
    def __init__(self, message=None, original_exception=None):
        self.message = message
        self.original_exception = original_exception

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

    def change_state(self, item, state, details=None):
        """
        Purpose of this method is when you batch publish now, we will first call all products with `change_state`
        and then all product `publish`.
        """

        item.publishing_status = state
        item.save()

        core_api_state = EbayProductPublishingStatus.core_api_state(state)
        if core_api_state is not None:
            try:
                self.user.core_api.send_state(item.product.inv_id, core_api_state, details=details)
            except HTTPError as e:
                raise PublishingSendStateFailedException()
        else:
            log.warn('Got state (%s) that cannot be mapped to core api PublishState', state)



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

    def publish(self, item):
        """
        Here this method can be called asynchronously, cause it loads everything from DB again
        :type item: EbayItemModel
        """

        service = EbayItems(self.user.account.token.ebay_object)
        try:
            response = service.publish(item.ebay_object)
        except EbayConnectionException as e:
            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=item,
                type=EbayApiAttemptType.PUBLISH
            )
            raise PublishingServiceException(e.message, original_exception=e)

        item.external_id = response.item_id
        item.published_at = response.start_time
        item.ends_at = response.end_time
        item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=service,
            item=item,
            type=EbayApiAttemptType.PUBLISH
        )

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


class UnpublishingService(PublishingUnpublishingService):
    def validate(self):
        if not self.product.is_published:
            raise PublishingValidationException(ugettext('Product is not published'))

    def get_item(self):
        return self.product.published_item

    def unpublish(self, item):

        service = EbayItems(self.user.account.token.ebay_object)
        try:
            response = service.unpublish(item.external_id)
        except EbayConnectionException as e:
            EbayApiAttempt.create_from_ebay_exception_for_item_and_type(
                exception=e,
                item=item,
                type=EbayApiAttemptType.UNPUBLISH
            )
            raise PublishingServiceException(e.message, original_exception=e)

        item.publishing_status = EbayProductPublishingStatus.UNPUBLISHED
        item.unpublished_at = response.end_time
        item.save()

        EbayApiAttempt.create_from_service_for_item_and_type(
            service=service,
            item=item,
            type=EbayApiAttemptType.UNPUBLISH
        )
