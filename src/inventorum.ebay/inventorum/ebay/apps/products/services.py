# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
from django.utils.functional import cached_property
from django.utils.translation import ugettext
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails, EbayItemPaymentMethod
from inventorum.ebay.lib.ebay.items import EbayItems


class PublishingServiceException(Exception):
    pass


class PublishingValidationException(PublishingServiceException):
    pass


class PublishingNotPossibleException(PublishingServiceException):
    pass


class PublishingService(object):
    def __init__(self, product_id, user):
        """
        Service for publishing products to ebay
        :type product_id: int
        :type user: EbayUserModel
        """
        self.product_id = product_id
        self.user = user
        self.core_info = self.user.core_api.get_account_info()
        self.core_account = self.core_info.account
        self.product, c = EbayProductModel.objects.get_or_create(inv_id=product_id, account=self.user.account)

    @cached_property
    def core_product(self):
        return self.user.core_api.get_product(self.product_id)

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
        # TODO: At this point we should inform API to change quantity I think?
        item = self._create_db_item()

    def publish(self):
        """
        Here this method can be called asynchronously, cause it loads everything from DB again
        """
        item = EbayItemModel.objects.get(product__inv_id=self.product_id)
        item.publishing_status = EbayProductPublishingStatus.IN_PROGRESS
        item.save()

        service = EbayItems(self.user.account.token.ebay_object)
        service.publish(item.ebay_object)

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
