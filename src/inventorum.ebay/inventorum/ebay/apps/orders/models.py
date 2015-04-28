# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from inventorum.ebay.lib.db.fields import MoneyField

from inventorum.ebay.lib.db.models import BaseModel, MappedInventorumModelQuerySet
from django.db import models
from inventorum.util.django.model_utils import PassThroughManager


log = logging.getLogger(__name__)


class OrderLineItem(BaseModel):
    """
    An order line item (a line item within an order) is the record of one buyer's commitment to purchase one or more
    *identical* items from the same listing.

    In the Trading API, this is also sometimes called a transaction for historical reasons.

    See: http://developer.ebay.com/Devzone/guides/ebayfeatures/Basics/eBay-BuildingBlocks.html#OrderLineItems
    """
    order = models.ForeignKey("orders.OrderModel", verbose_name="Order", related_name="line_items")

    # Generic reference to an orderable item (either `EbayItemModel` or `EbayItemVariationModel`)
    orderable_item_type = models.ForeignKey(ContentType)
    orderable_item_id = models.PositiveIntegerField()
    orderable_item_object = GenericForeignKey('orderable_item_type', 'orderable_item_id')

    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    unit_price = MoneyField(verbose_name="Unit price")


class OrderModelQuerySet(MappedInventorumModelQuerySet):
    pass


class OrderModel(BaseModel):
    inv_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="Universal inventorum id")
    ebay_id = models.CharField(max_length=255, verbose_name="Ebay id")

    objects = PassThroughManager.for_queryset_class(OrderModelQuerySet)()

    def __unicode__(self):
        return "[{} (inv_id: {}, ebay_id: {})] {}".format(self.pk, self.inv_id, self.ebay_id, self.__class__.__name__)


class OrderableItemModel(models.Model):
    """
    Mixin for item models that can be ordered (either `EbayItemModel` or `EbayItemVariationModel`)

    Note jm: We've to inherit here form models, otherwise django won't pick up the generic field.
    See: http://stackoverflow.com/questions/28115239/django-genericrelation-in-model-mixin
    """
    class Meta:
        abstract = True

    order_line_items = GenericRelation("orders.OrderLineItem",
                                       content_type_field="orderable_type",
                                       object_id_field="orderable_id")
