# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.translation import ugettext
from inventorum.ebay.apps.products.tasks import schedule_ebay_item_publish, schedule_ebay_item_unpublish
from requests.exceptions import RequestException

from rest_framework import exceptions, mixins
from rest_framework.response import Response
from rest_framework import status

from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.serializers import EbayProductSerializer, BatchPublishParametersSerializer
from inventorum.ebay.apps.products.services import PublishingValidationException, \
    PublishingCouldNotGetDataFromCoreAPI, PublishingPreparationService
from inventorum.ebay.lib.rest.exceptions import ApiException, BadRequest, NotFound

from inventorum.ebay.lib.rest.resources import APIResource


log = logging.getLogger(__name__)


class ProductResourceMixin(object):

    def get_or_create_product(self, inv_id, user):
        """
        Returns the product with the given `inv_id` for the given `account`.
        If the account has no product with such id, it is created lazily.

        :param inv_id: The global inventorum product id
        :param user: The user model in the ebay scope

        :type inv_id: int
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        :rtype: EbayProductModel
        """
        try:
            product = EbayProductModel.objects.get(inv_id=inv_id)
        except EbayProductModel.DoesNotExist:
            product = self._create_product_with_account_check(inv_id=inv_id, user=user)

        if product.account_id != user.account.id:
            raise NotFound(ugettext('Accessing product from another account is restricted'))

        return product

    def _create_product_with_account_check(self, inv_id, user):
        try:
            core_api = user.core_api.get_product(inv_id)
        except RequestException as e:
            if e.response.status_code == 404:
                raise NotFound("Core API returned 404")
            raise BadRequest("Core API error: {error}".format(error=e.message))

        product, c = EbayProductModel.objects.get_or_create(inv_id=inv_id, account=user.account)
        return product


    def _publish_product(self, product, request):
        preparation_service = PublishingPreparationService(product, user=request.user)
        try:
            preparation_service.validate()
        except PublishingValidationException as e:
            raise exceptions.ValidationError(e.message)
        except PublishingCouldNotGetDataFromCoreAPI as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                raise exceptions.NotFound
            raise ApiException(e.response.data, key="core.api.error", status_code=e.response.status_code)

        item = preparation_service.create_ebay_item()
        schedule_ebay_item_publish(ebay_item_id=item.id, context=self.get_task_execution_context())


class EbayProductResource(APIResource, ProductResourceMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    serializer_class = EbayProductSerializer

    def get_object(self):
        return self.get_or_create_product(self.kwargs["inv_product_id"], self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PublishResource(APIResource, ProductResourceMixin):
    serializer_class = EbayProductSerializer

    def post(self, request, inv_product_id):
        product = self.get_or_create_product(inv_product_id, request.user)

        self._publish_product(product, request)

        serializer = self.get_serializer(product)
        return Response(data=serializer.data)


class BatchPublishResource(APIResource, ProductResourceMixin):
    serializer_class = EbayProductSerializer

    def post(self, request):
        serializer = BatchPublishParametersSerializer(data=request.data, many=True,
                                                      context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        products = [d['product'] for d in data]

        errors = {}
        for product in products:
            try:
                self._publish_product(product, request)
            except exceptions.NotFound as e:
                errors[product.pk] = "Product %(id)s could not be found" % {'id': product.pk}
            except ApiException as e:
                errors[product.pk] = "Core Api returned error: %(error)s" % {'error': e.detail}
            except exceptions.ValidationError as e:
                errors[product.pk] = e.detail

        if errors:
            raise ApiException(errors, key='multiple.errors', status_code=400)

        serializer = self.get_serializer(products, many=True)
        return Response(data=serializer.data)


class UnpublishResource(APIResource, ProductResourceMixin):
    serializer_class = EbayProductSerializer
    lookup_url_kwarg = 'inv_product_id'
    lookup_field = 'inv_id'

    def get_queryset(self):
        return EbayProductModel.objects.filter(account=self.request.user.account)

    def post(self, request, inv_product_id):
        product = self.get_object()

        if not product.is_published:
            raise BadRequest(ugettext('Product is not published'))

        schedule_ebay_item_unpublish(ebay_item_id=product.published_item.id, context=self.get_task_execution_context())

        serializer = self.get_serializer(product)
        return Response(data=serializer.data)
