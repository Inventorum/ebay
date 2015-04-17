# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal

from django.utils.functional import cached_property
from django.utils.translation import ugettext
from inventorum.ebay.apps.products import EbayProductPublishingStatus, EbayItemUpdateStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod
from inventorum.ebay.lib.ebay.items import EbayItems
from requests.exceptions import HTTPError


log = logging.getLogger(__name__)


class PublishingServiceException(Exception):
    pass


class PublishingValidationException(PublishingServiceException):
    pass


class PublishingNotPossibleException(PublishingServiceException):
    pass


class PublishingCouldNotGetDataFromCoreAPI(PublishingServiceException):
    def __init__(self, response):
        self.response = response


class PublishingUnpublishingService(object):

    def __init__(self, product, user):
        """
        Abstract service for publishing/unpublishing products to ebay
        :type product: EbayProductModel
        :type user: EbayUserModel
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

    def prepare(self):
        """
        Create all necessary models for later publishing in async task
        :return:
        """
        item = self._create_db_item()
        # TODO: At this point we should change state in API to In progress of publishing, but api is not ready yet

        return item

    def publish(self, item):
        """
        Here this method can be called asynchronously, cause it loads everything from DB again
        :type item: EbayItemModel
        """
        item.publishing_status = EbayProductPublishingStatus.IN_PROGRESS
        item.save()

        service = EbayItems(self.user.account.token.ebay_object)
        response = service.publish(item.ebay_object)

        item.external_id = response.item_id
        item.publishing_status = EbayProductPublishingStatus.PUBLISHED
        item.published_at = response.start_time
        item.ends_at = response.end_time
        item.save()

        # TODO: At this point we should inform API to change quantity I think?

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

        return item


class UnpublishingService(PublishingUnpublishingService):

    def validate(self):
        if not self.product.is_published:
            raise PublishingValidationException(ugettext('Product is not published'))

    def unpublish(self):
        item = self.product.published_item

        service = EbayItems(self.user.account.token.ebay_object)
        response = service.unpublish(item.external_id)

        item.publishing_status = EbayProductPublishingStatus.UNPUBLISHED
        item.unpublished_at = response.end_time
        item.save()


class EbayItemUpdateService(object):

    def __init__(self, user, ebay_item_update):
        """
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        :type ebay_item_update: inventorum.ebay.apps.products.models.EbayItemUpdateModel
        """
        self.user = user
        self.ebay_item_update = ebay_item_update

    def update(self):
        self.ebay_item_update.status = EbayItemUpdateStatus.IN_PROGRESS

        service = EbayItems(self.user.account.token.ebay_object)
        response = service.revise_inventory_status(self.ebay_item_update.ebay_object)

        # TODO jm: Handle failures?

        self.ebay_item_update.status = EbayItemUpdateStatus.SUCCEEDED

    def _update_ebay_item(self):
        ebay_item = self.ebay_item_update.item
        assert isinstance(ebay_item, EbayItemModel)

        if self.ebay_item_update.has_updated_quantity:
            ebay_item.quantity = self.ebay_item_update.quantity

        if self.ebay_item_update.has_updated_gross_price:
            ebay_item.gross_price = self.ebay_item_update.gross_price

        ebay_item.save()
