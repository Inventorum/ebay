# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.products.serializers import EbayProductSerializer
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.rest.exceptions import BadRequest

from inventorum.ebay.lib.rest.resources import APIResource
from requests.exceptions import HTTPError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


log = logging.getLogger(__name__)


class PublishResource(APIResource):
    def post(self, request, inv_product_id):
        service = PublishingService(inv_product_id, request.user)
        try:
            service.validate()
        except PublishingValidationException as e:
            raise ValidationError(e.message)

        service.prepare()
        # TODO: Move this to celery task!
        try:
            service.publish()
        except EbayConnectionException as e:
            log.error('Got ebay errors: %s', e.errors)
            raise BadRequest([unicode(err) for err in e.errors])

        serializer = EbayProductSerializer(service.product)
        return Response(data=serializer.data)

        # TODO:
        # 3. async: publish ebay listing


