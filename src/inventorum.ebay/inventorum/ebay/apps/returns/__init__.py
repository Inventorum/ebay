# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.data.events import EbayEventReturned


log = logging.getLogger(__name__)


class EbayRefundType(object):
    """ Defines *supported* ebay refund types """

    EBAY = EbayEventReturned.RefundType.EBAY

    CHOICES = (
        (EBAY, "Refund by Ebay"),
    )
