# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging


log = logging.getLogger(__name__)


class EbayNotificationEventType(object):
    """
    A supported subset of the platform notifications that can be sent by ebay

    http://developer.ebay.com/Devzone/XML/docs/Reference/ebay/types/EbayNotificationEventType.html
    """
    # Sent each time a buyer purchases an item in a multiple-quantity, fixed-price listing
    FixedPriceTransaction = "FixedPriceTransaction"

    # Sent instead of 'FixedPriceTransaction' if a single-quantity, fixed-price listing is purchased
    ItemSold = "ItemSold"

    # Sent if a fixed-price listing ends with or without any sales
    ItemClosed = "ItemClosed"

    # Sent if eBay has administratively ended a listing for whatever reason
    ItemSuspended = "ItemSuspended"

    CHOICES = (
        (FixedPriceTransaction, "FixedPriceTransaction"),
        (ItemSold, "ItemSold"),
        (ItemClosed, "ItemClosed"),
        (ItemSuspended, "ItemSuspended")
    )


class EbayNotificationStatus(object):
    UNHANDLED = "unhandled"
    HANDLED = "handled"
    FAILED = "failed"

    CHOICES = (
        (UNHANDLED, "unhandled"),
        (HANDLED, "handled"),
        (FAILED, "failed")
    )
