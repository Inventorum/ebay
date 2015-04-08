# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.rest.resources import APIResource
from requests.exceptions import HTTPError
from rest_framework.response import Response


log = logging.getLogger(__name__)


class PublishResource(APIResource):

    def post(self, request, inv_product_id):
        try:
            core_product = request.user.core_api.get_product(inv_product_id)
        except HTTPError as e:
            log.warn('Got exception when trying to get product: %s', e)
            return Response(status=e.response.status_code)

        return Response(data=core_product.name)

        # TODO:
        # 1. sync: aggregate data, construct "ebay listing" (take from core product and ebay service)
        # 2. sync: validate "ebay listing"
        #   - is not already published
        #   - has billing address
        #   - has shipping services
        #   - has price >= 1
        #   - has category
        # 3. async: publish ebay listing
