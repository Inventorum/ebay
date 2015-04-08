# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayItemImageModel, \
    EbayItemShippingDetails


class PublishingValidationException(Exception):
    pass


class PublishingService(object):
    def __init__(self, product_id, user):
        """
        Service for publishing products to ebay
        :type product_id: int
        :type user: EbayUserModel
        """
        self.user = user
        self.core_product = self.user.core_api.get_product(product_id)
        self.core_info = self.user.core_api.get_account_info()
        self.core_account = self.core_info.account

    def validate(self):
        """
        Validates account and product before publishing to ebay
        :raises: PublishingValidationException
        """
        if not self.core_account.billing_address:
            raise PublishingValidationException(ugettext('To publish product we need your billing address'))

        if self.core_product.is_parent:
            raise PublishingValidationException(ugettext('Cannot publish products with variations'))

        if not self.core_product.shipping_services:
            raise PublishingValidationException(ugettext('Product has not shipping services selected'))

        try:
            product = EbayProductModel.objects.get(inv_id=self.core_product.id)
        except EbayProductModel.DoesNotExist:
            raise PublishingValidationException(ugettext('Couldnt find product [inv_id:%s] in database') % self.core_product.id)

        if not product.category_id:
            raise PublishingValidationException(ugettext('You need to select category'))

    def prepare(self):
        """
        Create all necessary models for later publishing in async task
        :return:
        """
        # TODO: At this point we should inform API to change quantity I think?
        item = self._create_db_item()

    def _create_db_item(self):

        db_product = EbayProductModel.objects.get(inv_id=self.core_product.id)

    # additional_cost = models.DecimalField(max_digits=20, decimal_places=10)
    # cost = models.DecimalField(max_digits=20, decimal_places=10)
    # service = models.CharField(max_length=255)
        item = EbayItemModel.objects.create(
            product=db_product,
            account=db_product.account,
            name=self.core_product.name,
            description=self.core_product.description,
            gross_price=self.core_product.gross_price,
            category=db_product.category,
            country=self.core_account.country,
            quantity=self.core_product.quantity,
            postal_code=self.core_account.billing_address.zipcode
        )

        for image in self.core_product.images:
            EbayItemImageModel.objects.create(
                inv_id=image.id,
                url=image.url,
                item=item
            )

        for service in self.core_product.shipping_services:
            EbayItemShippingDetails.objects.create(
                additional_cost=service.additional_cost,
                cost=service.cost,
                external_id=service.id,
                item=item
            )

        return item
