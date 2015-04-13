# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.serializers import EbayProductSerializer
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, \
    PublishingCouldNotGetDataFromCoreAPI, UnpublishingService
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.rest.exceptions import BadRequest, ApiException

from inventorum.ebay.lib.rest.resources import APIResource
from requests.exceptions import HTTPError
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status

log = logging.getLogger(__name__)


class PublishResource(APIResource):
    def post(self, request, inv_product_id):
        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=request.user.account)

        service = PublishingService(product, request.user)
        try:
            service.validate()
        except PublishingValidationException as e:
            raise exceptions.ValidationError(e.message)
        except PublishingCouldNotGetDataFromCoreAPI as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                raise exceptions.NotFound
            raise ApiException(e.response.data, key="core.api.error", status_code=e.response.status_code)

        item = service.prepare()
        # TODO: Move this to celery task!
        try:
            service.publish(item)
        except EbayConnectionException as e:
            log.error('Got ebay errors: %s', e.errors)
            raise BadRequest([unicode(err) for err in e.errors], key="ebay.api.errors")

        serializer = EbayProductSerializer(service.product)
        return Response(data=serializer.data)

        # TODO:
        # 3. async: publish ebay listing


class UnpublishResource(APIResource):
    def post(self, request, inv_product_id):
        try:
            product = EbayProductModel.objects.get(inv_id=inv_product_id, account=request.user.account)
        except EbayProductModel.DoesNotExist:
            raise exceptions.NotFound

        service = UnpublishingService(product, request.user)
        try:
            service.validate()
        except PublishingValidationException as e:
            raise exceptions.ValidationError(e.message)

        service.unpublish()
        serializer = EbayProductSerializer(service.product)
        return Response(data=serializer.data)




