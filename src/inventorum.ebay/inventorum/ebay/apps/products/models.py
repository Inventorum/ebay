# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel


log = logging.getLogger(__name__)


class EbayProductModel(MappedInventorumModel):
    """ Represents an inventorum product in the ebay context """
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="products",
                                verbose_name="Inventorum ebay account")
    category = models.ForeignKey("categories.CategoryModel", related_name="products", null=True, blank=True)


# Models for data just before publishing

class EbayItemImageModel(MappedInventorumModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="images")
    url = models.TextField()


class EbayItemModel(BaseModel):
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="items",
                                verbose_name="Inventorum ebay account")
    product = models.ForeignKey("products.EbayProductModel", related_name="images")
    category = models.ForeignKey("categories.CategoryModel", related_name="items")

    name = models.CharField(max_length=255)
    description = models.TextField()
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    gross_price = models.DecimalField(decimal_places=10, max_digits=20)
    publishing_status = models.IntegerField(choices=EbayProductPublishingStatus.CHOICES,
                                            default=EbayProductPublishingStatus.DRAFT)

    @classmethod
    def create_from_core_product(cls, core_product):
        """
        Create EbayProdyctModel from CoreProduct from API
        :param core_product: Core product from API
        :return: EbayProductModel
        :type core_product: inventorum.ebay.apps.core_api.models.CoreProduct
        """

        db_product = EbayProductModel.objects.get(inv_id=core_product.id)

        item = cls.objects.create(
            product=db_product,
            account=db_product.account,
            name=core_product.name,
            description=core_product.description,
            gross_price=core_product.gross_price,
            category=db_product.category
        )

        for image in core_product.images:
            EbayItemImageModel.objects.create(
                inv_id=image.id,
                url=image.url,
                item=item
            )
        return item


        # Description = serializers.SerializerMethodField('get_description')
        # Title = serializers.SerializerMethodField('get_title')
        # #
        # Currency = serializers.SerializerMethodField('get_currency')
        # Country = serializers.SerializerMethodField('get_country')
        # ListingDuration = serializers.SerializerMethodField('get_listing_duration')
        # PostalCode = serializers.SerializerMethodField('get_postal_code')
        #
        # PaymentMethods = serializers.SerializerMethodField('get_payment_methods')
        # PayPalEmailAddress = serializers.SerializerMethodField('get_paypal_email_address')
        # ListingType = serializers.SerializerMethodField('get_listing_type')
        #
        # Quantity = serializers.SerializerMethodField('get_quantity')
        # ConditionID = serializers.SerializerMethodField('get_condition_id')
        # StartPrice = serializers.SerializerMethodField('get_start_price')
        # DispatchTimeMax = serializers.SerializerMethodField('get_dispatch_time_max')
        #
        # PrimaryCategory = serializers.SerializerMethodField('get_primary_category')
        # ShippingDetails = serializers.SerializerMethodField('get_shipping_details')
        # ReturnPolicy = serializers.SerializerMethodField('get_return_policy')
        # PictureDetails = serializers.SerializerMethodField('get_picture_details')