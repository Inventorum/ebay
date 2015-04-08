# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from django_countries.fields import CountryField
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


class EbayItemShippingDetails(BaseModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="shipping")
    additional_cost = models.DecimalField(max_digits=20, decimal_places=10)
    cost = models.DecimalField(max_digits=20, decimal_places=10)
    external_id = models.CharField(max_length=255)

#     'ShippingDetails': [
#         {'ShippingServiceOptions': {
#             'ShippingServicePriority': 1,
#             'ShippingServiceAdditionalCost': 0.0,
#             'ShippingService': u'First service',
#             'ShippingServiceCost': 2.0}}],


class EbayItemModel(BaseModel):
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="items",
                                verbose_name="Inventorum ebay account")
    product = models.ForeignKey("products.EbayProductModel", related_name="items")
    category = models.ForeignKey("categories.CategoryModel", related_name="items")

    name = models.CharField(max_length=255)
    description = models.TextField()
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    gross_price = models.DecimalField(decimal_places=10, max_digits=20)
    publishing_status = models.IntegerField(choices=EbayProductPublishingStatus.CHOICES,
                                            default=EbayProductPublishingStatus.DRAFT)
    country = CountryField()