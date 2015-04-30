# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.inventory.serializers import SanityCheckEbaySerializer
from inventorum.ebay.apps.inventory.services import CoreApiQuantityCheck
from inventorum.ebay.apps.products.models import EbayItemModel
from rest_framework.response import Response
from inventorum.ebay.lib.rest.exceptions import BadRequest
from inventorum.ebay.lib.rest.resources import APIResource

log = logging.getLogger(__name__)


class SanityCheckResource(APIResource):
    serializer_class = SanityCheckEbaySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        ebay_sanity_check = serializer.instance

        quantity_check = CoreApiQuantityCheck(ebay_sanity_check.availabilities, request.user.account.ebay_location_id,
                                              request.user.core_api)
        ebay_sanity_check.availabilities = quantity_check.refresh_quantities()
        response_serializer = self.get_serializer(instance=ebay_sanity_check)
        return Response(data=response_serializer.data)