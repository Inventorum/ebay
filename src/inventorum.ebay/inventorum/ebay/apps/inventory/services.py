# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext as _

import logging
from inventorum.ebay.apps.products.models import EbayItemModel

log = logging.getLogger(__name__)


class CoreApiQuantityCheckBadLocation(Exception):
    pass


class CoreApiQuantityCheck(object):
    def __init__(self, data, location_id, core_api_client):
        """
        Checking if items ebay is asking for are still in stock
        :param data: list of items ebay is asking to check
        :param location_id: location of current location id to assert if products are owned by user
        :param core_api_client: client for core api
        :raises inventorum.ebay.apps.inventory.services.CoreApiQuantityCheckBadLocation
        :type data: list[inventorum.ebay.apps.inventory.models.EbayItemForQuantityCheck]
        :type location_id: unicode
        :type core_api_client: UserScopedCoreAPIClient
        """
        self.data = data
        self.location_id = location_id
        self.core_api_client = core_api_client

    def refresh_quantities(self):
        """
        Refreshing quantities from core api
        :rtype data: list[inventorum.ebay.apps.inventory.models.EbayItemForQuantityCheck]
        """
        product_ids = []
        ebay_items = {}
        for index, availability in enumerate(self.data):
            product_id = EbayItemModel.clean_sku(availability.sku)
            product_ids.append(product_id)
            ebay_items[product_id] = availability  # to later access it easily

            if not availability.LocationID == self.location_id:
                raise CoreApiQuantityCheckBadLocation(
                    _('Ebay\'s LocationID is not equal to currently authenticated account location id ("{0}" != "{1}")').format(
                        availability.LocationID, self.location_id))

        core_api_quantity = self.core_api_client.get_quantity_info(product_ids)

        for item in core_api_quantity:
            ebay_items[item.id].quantity = int(item.quantity)

        return self.data