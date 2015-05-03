# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django_countries.fields import CountryField
from django_extensions.db.fields.json import JSONField
from inventorum.ebay.lib.db.fields import MoneyField

from inventorum.ebay.lib.db.models import BaseModel, MappedInventorumModelQuerySet
from django.db import models
from inventorum.ebay.lib.ebay.data import CompleteStatusCodeType
from inventorum.util.django.model_utils import PassThroughManager


log = logging.getLogger(__name__)


class OrderLineItemModel(BaseModel):
    """
    An order line item (a line item within an order) is the record of one buyer's commitment to purchase one or more
    *identical* items from the same listing.

    In the Trading API, this is also sometimes called a transaction for historical reasons.

    See: http://developer.ebay.com/Devzone/guides/ebayfeatures/Basics/eBay-BuildingBlocks.html#OrderLineItems
    """
    order = models.ForeignKey("orders.OrderModel", verbose_name="Order", related_name="line_items")

    ebay_id = models.CharField(max_length=255, verbose_name="Ebay transaction id")

    # Generic reference to an orderable item (either `EbayItemModel` or `EbayItemVariationModel`)
    orderable_item_type = models.ForeignKey(ContentType)
    orderable_item_id = models.PositiveIntegerField()
    orderable_item = GenericForeignKey('orderable_item_type', 'orderable_item_id')

    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    unit_price = MoneyField(verbose_name="Unit price")

    @property
    def inv_product_id(self):
        return self.orderable_item.inv_product_id


class OrderModelQuerySet(MappedInventorumModelQuerySet):

    def by_account(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :rtype: OrderModelQuerySet
        """
        return self.filter(account_id=account.id)


class OrderModel(BaseModel):
    account = models.ForeignKey("accounts.EbayAccountModel", verbose_name="Ebay account")

    inv_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="Universal inventorum id")

    ebay_id = models.CharField(unique=True, max_length=255, verbose_name="Ebay id")
    ebay_status = models.CharField(max_length=255, choices=CompleteStatusCodeType.CHOICES,
                                   verbose_name="Ebay order status")
    original_ebay_data = JSONField(verbose_name="Original ebay data", null=True)

    buyer_first_name = models.CharField(max_length=255)
    buyer_last_name = models.CharField(max_length=255)
    buyer_email = models.CharField(max_length=255)

    shipping_first_name = models.CharField(max_length=255, null=True, blank=True)
    shipping_last_name = models.CharField(max_length=255, null=True, blank=True)
    shipping_address1 = models.CharField(max_length=255, null=True, blank=True)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255, null=True, blank=True)
    shipping_postal_code = models.CharField(max_length=255, null=True, blank=True)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = CountryField(null=True, blank=True)

    selected_shipping_service = models.CharField(max_length=255, null=True, blank=True)
    selected_shipping_cost = MoneyField(null=True, blank=True)

    # the total cost of all order line items, does not include any shipping/handling, insurance, or sales tax costs.
    subtotal = MoneyField(null=True, blank=True)
    # equals the subtotal value plus the shipping/handling, shipping insurance, and sales tax costs.
    total = MoneyField(null=True, blank=True)

    payment_method = models.CharField(max_length=255, null=True, blank=True)
    payment_amount = MoneyField(null=True, blank=True)
    payment_status = models.CharField(max_length=255, null=True, blank=True)

    objects = PassThroughManager.for_queryset_class(OrderModelQuerySet)()

    def __unicode__(self):
        return "{} (inv_id: {}, ebay_id: {})".format(self.pk, self.inv_id, self.ebay_id)

    @property
    def created_in_core_api(self):
        return self.inv_id is not None


class OrderableItemModel(models.Model):
    """
    Mixin for item models that can be ordered (either `EbayItemModel` or `EbayItemVariationModel`)

    Note jm: We've to inherit here form models, otherwise django won't pick up the generic field.
    See: http://stackoverflow.com/questions/28115239/django-genericrelation-in-model-mixin
    """
    class Meta:
        abstract = True

    order_line_items = GenericRelation("orders.OrderLineItemModel",
                                       content_type_field="orderable_item_type",
                                       object_id_field="orderable_item_id")

    @property
    def inv_product_id(self):
        """
        Must be defined by implementing classes either through a property or a model field
        (http://stackoverflow.com/questions/1151212/equivalent-of-notimplementederror-for-fields-in-python)

        :rtype: int
        """
        raise NotImplementedError
