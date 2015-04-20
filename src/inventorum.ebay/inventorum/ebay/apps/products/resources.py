# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework import exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.serializers import EbayProductSerializer
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, \
    PublishingCouldNotGetDataFromCoreAPI, UnpublishingService
from inventorum.ebay.apps.products.tasks import foo
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.rest.exceptions import BadRequest, ApiException

from inventorum.ebay.lib.rest.resources import APIResource


log = logging.getLogger(__name__)


class ProductResourceMixin(object):

    def get_or_create_product(self, inv_id, account):
        """
        Returns the product with the given `inv_id` for the given `account`.
        If the account has no product with such id, it is created lazily.

        :param inv_id: The global inventorum product id
        :param account: The account model in the ebay scope

        :type inv_id: int
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :rtype: EbayProductModel
        """
        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_id, account=account)
        return product


class EbayProductResource(APIResource, ProductResourceMixin):
    serializer_class = EbayProductSerializer

    def put(self, request, inv_product_id):
        product = self.get_or_create_product(inv_product_id, request.user.account)

        serializer = self.get_serializer(product, data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data)


class PublishResource(APIResource, ProductResourceMixin):
    serializer_class = EbayProductSerializer

    def post(self, request, inv_product_id):
        product = self.get_or_create_product(inv_product_id, request.user.account)

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

        foo.delay(context=TaskExecutionContext(user_id=1, account_id=1, request_id=1245))

        try:
            service.publish(item)
        except EbayConnectionException as e:
            log.error('Got ebay errors: %s', e.errors)
            raise BadRequest([unicode(err) for err in e.errors], key="ebay.api.errors")

        serializer = self.get_serializer(service.product)
        return Response(data=serializer.data)

        # TODO:
        # 3. async: publish ebay listing


class UnpublishResource(APIResource, ProductResourceMixin):
    serializer_class = EbayProductSerializer
    lookup_url_kwarg = 'inv_product_id'
    lookup_field = 'inv_id'

    def get_queryset(self):
        return EbayProductModel.objects.filter(account=self.request.user.account)

    def post(self, request, inv_product_id):
        product = self.get_object()

        service = UnpublishingService(product, request.user)
        try:
            service.validate()
        except PublishingValidationException as e:
            raise exceptions.ValidationError(e.message)

        service.unpublish()
        serializer = self.get_serializer(service.product)
        return Response(data=serializer.data)
