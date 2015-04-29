# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import Ebay
from ebaysdk.inventorymanagement import Connection as InventoryManagementConnection
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayAddLocationResponseDeserializer, \
    EbayAddInventoryResponseDeserializer


class EbayInventoryManagement(Ebay):
    default_connection_cls = InventoryManagementConnection

    def add_location(self, location):
        """
        :type location: inventorum.ebay.lib.ebay.data.inventorymanagement.EbayLocation
        :rtype: EbayAddLocationResponse
        """
        response = self.execute('AddInventoryLocation', location.dict())
        return EbayAddLocationResponseDeserializer(data=response).build()

    def add_inventory(self, sku, locations_availability):
        """
        :type sku: unicode
        :type locations: list[inventorum.ebay.lib.ebay.data.inventorymanagement.EbayLocationAvailability]
        :rtype: inventorum.ebay.lib.ebay.data.inventorymanagement.EbayAddInventoryResponse
        """
        response = self.execute('AddInventory', {
            "SKU": sku,
            "Locations": {
                "Location": [l.dict() for l in locations_availability]
            }
        })
        return EbayAddInventoryResponseDeserializer(data=response).build()
