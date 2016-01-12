# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from inventorum_ebay.apps.returns import EbayRefundType, ReturnsAcceptedOption
from inventorum_ebay.lib.db.models import MappedInventorumModel, BaseModel

from inventorum_ebay.lib.db.fields import MoneyField
from inventorum_ebay.lib.ebay.data.items import EbayReturnPolicy


log = logging.getLogger(__name__)


class ReturnItemModel(MappedInventorumModel):
    order_line_item = models.ForeignKey("orders.OrderLineItemModel", related_name="return_items")
    return_model = models.ForeignKey("returns.ReturnModel", related_name="items")
    refund_amount = MoneyField()
    refund_quantity = models.IntegerField()


class ReturnModel(MappedInventorumModel):
    order = models.ForeignKey("orders.OrderModel", related_name="returns")
    synced_with_ebay = models.BooleanField(default=False)

    refund_type = models.CharField(max_length=255, choices=EbayRefundType.CHOICES)
    refund_amount = MoneyField()

    refund_note = models.TextField(default="")


class ReturnPolicyModel(BaseModel):
    returns_accepted_option = models.CharField(max_length=255, null=True, blank=True)
    returns_within_option = models.CharField(max_length=255, null=True, blank=True)
    shipping_cost_paid_by_option = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    @property
    def is_defined(self):
        """
        :rtype: bool
        """
        return self.returns_accepted_option is not None

    @property
    def returns_accepted(self):
        """
        :rtype: bool
        """
        return self.returns_accepted_option == ReturnsAcceptedOption.ReturnsAccepted

    @property
    def ebay_object(self):
        """
        :rtype: bool
        """
        ebay_return_policy_kwargs = dict(returns_accepted_option=self.returns_accepted_option)

        if self.returns_accepted:
            ebay_return_policy_kwargs.update(returns_within_option=self.returns_within_option,
                                             shipping_cost_paid_by_option=self.shipping_cost_paid_by_option,
                                             description=self.description)

        return EbayReturnPolicy(**ebay_return_policy_kwargs)
