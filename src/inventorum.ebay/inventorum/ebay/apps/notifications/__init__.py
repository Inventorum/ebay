# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging


log = logging.getLogger(__name__)


class NotificationEventTypeCodeType(object):
    """
    Platform notifications that can be sent by ebay and are handled/supported by our system

    http://developer.ebay.com/Devzone/XML/docs/Reference/ebay/types/NotificationEventTypeCodeType.html
    """

    # Sent each time a buyer purchases an item in a multiple-quantity, fixed-price listing
    FixedPriceTransaction = "FixedPriceTransaction"

    # Sent instead of 'FixedPriceTransaction' if a single-quantity, fixed-price listing is purchased
    ItemSold = "ItemSold"

    # Sent if a fixed-price listing ends with no sales
    ItemClosed = "ItemClosed"

    # Sent if eBay has administratively ended a listing for whatever reason
    ItemSuspended = "ItemSuspended"
