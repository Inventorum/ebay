# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.lib.ebay import Ebay
from ebaysdk.inventorymanagement import Connection as InventoryManagementConnection
from inventorum_ebay.lib.ebay.data.inventorymanagement import EbayAddLocationResponseDeserializer, \
    EbayAddDeleteInventoryResponseDeserializer, EbayDeleteInventoryLocationDeserializer


class EbayInventoryManagement(Ebay):
    default_connection_cls = InventoryManagementConnection

    def add_location(self, location):
        """
        :type location: inventorum_ebay.lib.ebay.data.inventorymanagement.EbayLocation
        :rtype: EbayAddLocationResponse
        """
        response = self.execute('AddInventoryLocation', location.dict())
        return EbayAddLocationResponseDeserializer(data=response).build()

    def add_inventory(self, sku, locations_availability):
        """
        :type sku: unicode
        :type locations: list[inventorum_ebay.lib.ebay.data.inventorymanagement.EbayLocationAvailability]
        :rtype: inventorum_ebay.lib.ebay.data.inventorymanagement.EbayAddDeleteInventoryResponse
        """
        response = self.execute('AddInventory', {
            "SKU": sku,
            "Locations": {
                "Location": [l.dict() for l in locations_availability]
            }
        })
        return EbayAddDeleteInventoryResponseDeserializer(data=response).build()

    def delete_inventory(self, sku, delete_all, locations_ids=None):
        assert delete_all or locations_ids, "If you do not specify locations, you need to delete all"
        locations_ids = locations_ids or []

        response = self.execute('DeleteInventory', {
            'SKU': sku,
            'Confirm': unicode(delete_all).lower(),
            'Locations': {
                'Location': [{'LocationID': location_id} for location_id in locations_ids]
            }
        })
        return EbayAddDeleteInventoryResponseDeserializer(data=response).build()

    def delete_location(self, location_id):
        """
        :param location_id: unicode
        :rtype: inventorum_ebay.lib.ebay.data.inventorymanagement.EbayDeleteInventoryLocationResponse
        """
        response = self.execute('DeleteInventoryLocation', {
            'LocationID': location_id
        })
        return EbayDeleteInventoryLocationDeserializer(data=response).build()
