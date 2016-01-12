# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django_extensions.db.fields.json import JSONField
from inventorum_ebay.apps.orders import CorePaymentMethod, PickupCode
from inventorum_ebay.apps.shipping import INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID
from inventorum_ebay.lib.db.fields import MoneyField, TaxRateField

from inventorum_ebay.lib.db.models import BaseModel, MappedInventorumModelQuerySet
from django.db import models
from inventorum_ebay.lib.ebay.data import CompleteStatusCodeType
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
    inv_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="Universal inventorum id")

    # Generic reference to an orderable item (either `EbayItemModel` or `EbayItemVariationModel`)
    orderable_item_type = models.ForeignKey(ContentType)
    orderable_item_id = models.PositiveIntegerField()
    orderable_item = GenericForeignKey('orderable_item_type', 'orderable_item_id')

    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    unit_price = MoneyField(verbose_name="Unit price")
    tax_rate = TaxRateField(verbose_name="Tax rate")

    @property
    def inv_product_id(self):
        return self.orderable_item.inv_product_id

    @property
    def transaction_id(self):
        """
        :rtype: unicode
        """
        return self.ebay_id


class OrderModelQuerySet(MappedInventorumModelQuerySet):

    def by_account(self, account):
        """
        :type account: inventorum_ebay.apps.accounts.models.EbayAccountModel
        :rtype: OrderModelQuerySet
        """
        return self.filter(account_id=account.id)


class OrderModel(BaseModel):
    account = models.ForeignKey("accounts.EbayAccountModel", verbose_name="Ebay account")

    ebay_id = models.CharField(unique=True, max_length=255, verbose_name="Ebay id")
    ebay_complete_status = models.CharField(max_length=255, choices=CompleteStatusCodeType.CHOICES,
                                            verbose_name="Ebay order status")
    original_ebay_data = JSONField(verbose_name="Original ebay data", null=True)

    inv_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="Universal inventorum id")

    buyer_first_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_last_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_email = models.CharField(max_length=255, null=True, blank=True)

    shipping_address = models.OneToOneField("accounts.AddressModel", null=True, blank=True,
                                            related_name="shipping_order")
    billing_address = models.OneToOneField("accounts.AddressModel", null=True, blank=True,
                                           related_name="billing_order")

    selected_shipping = models.OneToOneField("shipping.ShippingServiceConfigurationModel", related_name="order",
                                             null=True, blank=True)

    # the total cost of all order line items, does not include any shipping/handling, insurance, or sales tax costs.
    subtotal = MoneyField(null=True, blank=True)
    # equals the subtotal value plus the shipping/handling, shipping insurance, and sales tax costs.
    total = MoneyField(null=True, blank=True)

    payment_method = models.CharField(max_length=255, choices=CorePaymentMethod.CHOICES, null=True, blank=True)
    payment_amount = MoneyField(null=True, blank=True)
    ebay_payment_method = models.CharField(max_length=255, null=True, blank=True)
    ebay_payment_status = models.CharField(max_length=255, null=True, blank=True)

    # represents the status in the core api (presence of related enforced by `OrderFactory`)
    """:type: OrderStatusModel"""
    core_status = models.OneToOneField("orders.OrderStatusModel", related_name="core_status_related_order")
    # represents the status on the ebay side (presence of related enforced by `OrderFactory`)
    """:type: OrderStatusModel"""
    ebay_status = models.OneToOneField("orders.OrderStatusModel", related_name="ebay_status_related_order")

    # click and collect related attributes
    pickup_code = models.CharField(max_length=PickupCode.LENGTH, null=True, blank=True)

    objects = PassThroughManager.for_queryset_class(OrderModelQuerySet)()

    def __unicode__(self):
        return "{} (inv_id: {}, ebay_id: {})".format(self.pk, self.inv_id, self.ebay_id)

    @property
    def created_in_core_api(self):
        return self.inv_id is not None

    @property
    def is_click_and_collect(self):
        return self.selected_shipping and self.selected_shipping.service.external_id == INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # since there is a strong connection between the order model and its ebay/core status,
        # we save these models here as well for convenience and to avoid simple programming errors.
        if self.core_status:
            self.core_status.save()

        if self.ebay_status:
            self.ebay_status.save()

        if self.is_click_and_collect and not self.pickup_code:
            self.pickup_code = self.generate_unique_pickup_code(account=self.account)

        return super(OrderModel, self).save(force_insert, force_update, using, update_fields)

    @classmethod
    def generate_unique_pickup_code(cls, account):
        """
        :type account: inventorum_ebay.apps.accounts.models.EbayAccountModel
        :rtype: unicode
        """
        found_unique = False
        while not found_unique:
            pickup_code = PickupCode.generate_random()
            found_unique = not cls.objects.filter(account=account, pickup_code=pickup_code).exists()

        return pickup_code


class OrderFactory(object):
    """ Responsible for creating order models with proper relations """

    @classmethod
    def create(cls, account, ebay_id, ebay_complete_status, **kwargs):
        """
        :type account: inventorum_ebay.apps.accounts.models.EbayAccountModel
        :type ebay_id: unicode
        :type ebay_complete_status: unicode

        :rtype: OrderModel
        """
        core_status = kwargs.pop("core_status", None)
        if core_status is None:
            core_status = OrderStatusModel.objects.create()

        ebay_status = kwargs.pop("ebay_status", None)
        if ebay_status is None:
            ebay_status = OrderStatusModel.objects.create()

        return OrderModel.objects.create(account=account, ebay_id=ebay_id, ebay_complete_status=ebay_complete_status,
                                         core_status=core_status, ebay_status=ebay_status, **kwargs)


class OrderStatusModel(BaseModel):
    is_paid = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)

    @property
    def is_ready_for_pickup(self):
        return self.order.is_click_and_collect and self.is_shipped

    @property
    def is_picked_up(self):
        return self.order.is_click_and_collect and self.is_delivered

    @property
    def is_pickup_canceled(self):
        return self.order.is_click_and_collect and self.is_canceled

    @property
    def order(self):
        """
        :rtype: OrderModel
        """
        # Note jm: Unfortunately, there is no other way as two one-to-one relations cannot have the same related name
        return getattr(self, "core_status_related_order", None) or getattr(self, "ebay_status_related_order", None)


class OrderableItemModel(models.Model):
    """
    Mixin for item models that can be ordered (either `EbayItemModel` or `EbayItemVariationModel`)

    Note jm: We've to inherit here form models, otherwise django won't pick up the generic field.
    See: http://stackoverflow.com/questions/28115239/django-genericrelation-in-model-mixin
    """
    class Meta:
        abstract = True

    inv_product_id = models.BigIntegerField(verbose_name="Inventorum product id")
    order_line_items = GenericRelation("orders.OrderLineItemModel",
                                       content_type_field="orderable_item_type",
                                       object_id_field="orderable_item_id")

    @property
    def ebay_item_id(self):
        raise NotImplementedError
