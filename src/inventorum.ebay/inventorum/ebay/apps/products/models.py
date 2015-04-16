# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from django_countries.fields import CountryField
from inventorum.ebay import settings
from inventorum.ebay.apps.categories.models import CategorySpecificModel
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel
from inventorum.ebay.lib.ebay.data.items import EbayShippingService, EbayFixedPriceItem, EbayPicture


log = logging.getLogger(__name__)


class EbayProductModel(MappedInventorumModel):
    """ Represents an inventorum product in the ebay context """
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="products",
                                verbose_name="Inventorum ebay account")
    category = models.ForeignKey("categories.CategoryModel", related_name="products", null=True, blank=True)
    external_item_id = models.CharField(max_length=255, null=True, blank=True)

    @property
    def is_published(self):
        return self.published_item is not None

    @property
    def published_item(self):
        try:
            return self.items.get(publishing_status=EbayProductPublishingStatus.PUBLISHED)
        except EbayItemModel.DoesNotExist:
            return None

    @property
    def external_item_id(self):
        published_item = self.published_item

        if not published_item:
            return None

        return published_item.external_id

    @property
    def listing_url(self):
        published_item = self.published_item

        if not published_item:
            return None

        return settings.EBAY_LISTING_URL.format(listing_id=published_item.external_id)

    @property
    def specific_values_for_current_category(self):
        return self.specific_values.filter(specific__category_id=self.category_id)


# Models for data just before publishing

class EbayItemImageModel(MappedInventorumModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="images")
    url = models.TextField()

    @property
    def ebay_object(self):
        return EbayPicture(self.url.replace('https://', 'http://'))


class EbayItemShippingDetails(BaseModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="shipping")
    additional_cost = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    cost = models.DecimalField(max_digits=20, decimal_places=10)
    external_id = models.CharField(max_length=255)

    @property
    def ebay_object(self):
        return EbayShippingService(
            id=self.external_id,
            cost=self.cost,
            additional_cost=self.additional_cost
        )


class EbayItemPaymentMethod(BaseModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="payment_methods")
    external_id = models.CharField(max_length=255)


class EbayItemModel(BaseModel):
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="items",
                                verbose_name="Inventorum ebay account")
    product = models.ForeignKey("products.EbayProductModel", related_name="items")
    category = models.ForeignKey("categories.CategoryModel", related_name="items")

    name = models.CharField(max_length=255)
    listing_duration = models.CharField(max_length=255)
    description = models.TextField()
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    gross_price = models.DecimalField(decimal_places=10, max_digits=20)
    paypal_email_address = models.CharField(max_length=255, null=True, blank=True)
    publishing_status = models.IntegerField(choices=EbayProductPublishingStatus.CHOICES,
                                            default=EbayProductPublishingStatus.DRAFT)

    published_at = models.DateTimeField(null=True, blank=True)
    unpublished_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    external_id = models.CharField(max_length=255, null=True, blank=True)
    country = CountryField()

    @property
    def ebay_object(self):
        payment_methods = list(self.payment_methods.all().values_list('external_id', flat=True))
        return EbayFixedPriceItem(
            title=self.name,
            description=self.description,
            listing_duration=self.listing_duration,
            country=unicode(self.country),
            postal_code=self.postal_code,
            quantity=self.quantity,
            start_price=self.gross_price,
            paypal_email_address=self.paypal_email_address,
            payment_methods=payment_methods,
            category_id=self.category.external_id,
            shipping_services=[s.ebay_object for s in self.shipping.all()],
            pictures=[i.ebay_object for i in self.images.all()],
        )


class EbayProductSpecificModel(BaseModel):
    product = models.ForeignKey(EbayProductModel, related_name="specific_values")
    specific = models.ForeignKey(CategorySpecificModel, related_name="+")
    value = models.CharField(max_length=255)