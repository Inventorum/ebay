# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data.shipping import EbayShippingService

log = logging.getLogger(__name__)


class EbayDetails(EbayTrading):

    def get_shipping_services(self):
        response = self._get_details("ShippingServiceDetails")
        return EbayShippingService.create_from_data(response.get("ShippingServiceDetails", []))

    def _get_details(self, detail_name):
        """
        :type detail_name: unicode
        :rtype: dict
        """
        return self.execute("GeteBayDetails", {
            "DetailName": detail_name
        })
