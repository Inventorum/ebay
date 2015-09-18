# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.translation import ugettext_lazy as _
from inventorum.ebay.lib.ebay.data.events import EbayEventReturned


log = logging.getLogger(__name__)


class EbayRefundType(object):
    """ Defines *supported* ebay refund types """

    EBAY = EbayEventReturned.RefundType.EBAY

    CHOICES = (
        (EBAY, "Refund by Ebay"),
    )


class ReturnsAcceptedOption(object):
    ReturnsAccepted = 'ReturnsAccepted'
    ReturnsNotAccepted = 'ReturnsNotAccepted'

    CHOICES = sorted([(ReturnsAccepted, _(ReturnsAccepted)),
                      (ReturnsNotAccepted, _(ReturnsNotAccepted))])


class ReturnsWithinOption(object):
    Days_14 = 'Days_14'
    Months_1 = 'Months_1'

    CHOICES = sorted([(Days_14, _(Days_14)),
                      (Months_1, _(Months_1))])


class ShippingCostPaidByOption(object):
    Buyer = 'Buyer'
    Seller = 'Seller'

    CHOICES = sorted([(Buyer, _(Buyer)),
                      (Seller, _(Seller))])
