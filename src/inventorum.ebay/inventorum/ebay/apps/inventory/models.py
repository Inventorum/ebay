# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayAvailability

log = logging.getLogger(__name__)


class CoreQuantity(object):
    def __init__(self, id, quantity):
        self.id = id
        self.quantity = quantity


class EbaySanityCheck(object):
    def __init__(self, trackingUUID, availabilities):
        self.trackingUUID = trackingUUID
        self.availabilities = availabilities

class EbayItemForQuantityCheck(object):
    def __init__(self, sku, LocationID, quantity):
        self.sku = sku
        self.LocationID = LocationID
        self.quantity = quantity

    @property
    def available(self):
        return EbayAvailability.IN_STOCK if self.quantity > 0 else EbayAvailability.OUT_OF_STOCK
