# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models
from inventorum.ebay.apps.returns import EbayRefundType
from inventorum.ebay.lib.db.models import MappedInventorumModel

from inventorum.ebay.lib.db.fields import MoneyField


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
