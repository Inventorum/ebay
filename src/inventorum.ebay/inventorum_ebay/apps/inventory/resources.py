# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from django.db import transaction

from inventorum_ebay.apps.inventory.serializers import SanityCheckEbaySerializer
from inventorum_ebay.apps.inventory.services import CoreApiQuantityCheck
from rest_framework.response import Response
from inventorum_ebay.lib.rest.resources import PublicAPIResource

log = logging.getLogger(__name__)


class SanityCheckResource(PublicAPIResource):
    serializer_class = SanityCheckEbaySerializer

    @transaction.atomic
    def post(self, request):
        log.info('Sanity check from ebay: request: %s', request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        ebay_sanity_check = serializer.instance

        quantity_check = CoreApiQuantityCheck(ebay_sanity_check.availabilities, request.user.account.ebay_location_id,
                                              request.user.core_api)
        ebay_sanity_check.availabilities = quantity_check.refresh_quantities()
        response_serializer = self.get_serializer(instance=ebay_sanity_check)
        data = response_serializer.data
        log.info('Sanity check from ebay: response: %s', data)
        return Response(data=data)
