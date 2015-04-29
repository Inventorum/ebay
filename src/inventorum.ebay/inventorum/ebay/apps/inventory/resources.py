# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.inventory.serializers import SanityCheckEbaySerializer
from inventorum.ebay.apps.products.models import EbayItemModel

from rest_framework.response import Response

from inventorum.ebay.lib.rest.exceptions import BadRequest

from inventorum.ebay.lib.rest.resources import APIResource


log = logging.getLogger(__name__)


class SanityCheckResource(APIResource):
    def post(self, request):
        serializer = SanityCheckEbaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        product_ids = []
        ebay_items = {}

        for index, availability in enumerate(data['availabilities']):
            product_id = EbayItemModel.clean_sku(availability['sku'])
            product_ids.append(product_id)
            ebay_items[product_id] = availability  # to later access it easily
            ebay_items[product_id]['index'] = index

            if not availability['LocationID'] == request.user.account.ebay_location_id:
                raise BadRequest(
                    'Ebay\'s LocationID is not equal to currently authenticated account location id ("{0}" != "{1}")'.format(
                        availability['LocationID'], request.user.account.ebay_location_id))

        core_api_quantity = request.user.core_api.get_quantity_info(product_ids)

        for item in core_api_quantity:
            ebay_item_index = ebay_items[item.id]['index']
            data['availabilities'][ebay_item_index]['quantity'] = int(item.quantity)

        response_serializer = SanityCheckEbaySerializer(data=data)
        response_serializer.is_valid(raise_exception=True)
        return Response(data=response_serializer.data)