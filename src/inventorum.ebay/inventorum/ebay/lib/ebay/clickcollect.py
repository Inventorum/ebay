# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import EbayAddLocationResponseDeserializer, Ebay
from ebaysdk.inventorymanagement import Connection as InventoryManagementConnection


class EbayInventoryManagement(Ebay):
    default_connection_cls = InventoryManagementConnection

    def add_location(self, location):
        """
        :type location: inventorum.ebay.lib.ebay.data.inventorymanagement.EbayLocation
        :rtype: EbayAddLocationResponse
        """
        response = self.execute('AddInventoryLocation', location.dict())
        return EbayAddLocationResponseDeserializer(data=response).build()
