# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.lib.db.models import MappedInventorumModel


log = logging.getLogger(__name__)


class EbayImageModel(MappedInventorumModel):
    product = models.ForeignKey("products.EbayProductModel", related_name="images")
    url = models.TextField()


class EbayProductModel(MappedInventorumModel):
    """ Represents an inventorum product in the ebay context """
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="products",
                                verbose_name="Inventorum ebay account")

    name = models.CharField(max_length=255)
    description = models.TextField()
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    gross_price = models.DecimalField(decimal_places=10, max_digits=20)
    category = models.ForeignKey("categories.CategoryModel", related_name="products")
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

        product = cls.objects.create(
            name=core_product.name,
            inv_id=core_product.id,
            description=core_product.description,
            gross_price=core_product.gross_price,
        )

        images_db = []
        for image in core_product.images:
            images_db.append(EbayImageModel.objects.create(
                inv_id=image.id,
                url=image.url
            ))
        product.images.add(*images_db)
        return product


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