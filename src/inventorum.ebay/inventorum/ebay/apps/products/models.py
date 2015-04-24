# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
import logging

from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurable

import jsonfield
from django.db import models
from django_countries.fields import CountryField
from django_extensions.db.fields.json import JSONField
from inventorum.ebay import settings

from inventorum.ebay.apps.categories.models import CategorySpecificModel
from inventorum.ebay.apps.products import EbayItemUpdateStatus, EbayApiAttemptType, EbayItemPublishingStatus
from inventorum.ebay.lib.db.models import MappedInventorumModel, BaseModel, BaseQuerySet, MappedInventorumModelQuerySet
from inventorum.ebay.lib.ebay.data import EbayParser
from inventorum.ebay.lib.ebay.data.items import EbayItemShippingService, EbayFixedPriceItem, EbayPicture, EbayItemSpecific, \
    EbayReviseFixedPriceItem
from inventorum.util.django.model_utils import PassThroughManager


log = logging.getLogger(__name__)


class EbayProductModelQuerySet(MappedInventorumModelQuerySet):

    def published(self):
        """
        :rtype: EbayProductModelQuerySet
        """
        return self.filter(items__publishing_status=EbayItemPublishingStatus.PUBLISHED).distinct()

    def by_account(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :rtype: EbayProductModelQuerySet
        """
        return self.filter(account=account)


class EbayProductModel(ShippingServiceConfigurable, MappedInventorumModel):
    """ Represents an inventorum product in the ebay context """
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="products",
                                verbose_name="Inventorum ebay account")
    category = models.ForeignKey("categories.CategoryModel", related_name="products", null=True, blank=True)
    external_item_id = models.CharField(max_length=255, null=True, blank=True)

    deleted_in_core_api = models.BooleanField(default=False)

    objects = PassThroughManager.for_queryset_class(EbayProductModelQuerySet)()

    @property
    def is_published(self):
        return self.published_item is not None

    @property
    def published_item(self):
        try:
            return self.items.get(publishing_status=EbayItemPublishingStatus.PUBLISHED)
        except EbayItemModel.DoesNotExist:
            return None

    @property
    def external_item_id(self):
        published_item = self.published_item

        if not published_item:
            return None

        return published_item.external_id

    @property
    def listing_url(self):
        published_item = self.published_item

        if not published_item:
            return None

        return settings.EBAY_LISTING_URL.format(listing_id=published_item.external_id)

    @property
    def specific_values_for_current_category(self):
        return self.specific_values.filter(specific__category_id=self.category_id)


# Models for data just before publishing

class EbayItemImageModel(MappedInventorumModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="images")
    url = models.TextField()

    @property
    def ebay_object(self):
        return EbayPicture(self.url.replace('https://', 'http://'))


class EbayItemShippingDetails(BaseModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="shipping")
    additional_cost = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    cost = models.DecimalField(max_digits=20, decimal_places=10)
    external_id = models.CharField(max_length=255)

    @property
    def ebay_object(self):
        return EbayItemShippingService(
            id=self.external_id,
            cost=self.cost,
            additional_cost=self.additional_cost
        )


class EbayItemPaymentMethod(BaseModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="payment_methods")
    external_id = models.CharField(max_length=255)


class EbayItemModelQuerySet(BaseQuerySet):

    def get_for_publishing(self, **kwargs):
        """
        :rtype EbayItemModelQuerySet
        """
        return self.select_related("product", "shipping", "images", "specific_values").get(**kwargs)


class EbayItemModel(BaseModel):
    account = models.ForeignKey("accounts.EbayAccountModel", related_name="items",
                                verbose_name="Inventorum ebay account")
    product = models.ForeignKey("products.EbayProductModel", related_name="items")
    category = models.ForeignKey("categories.CategoryModel", related_name="items")

    name = models.CharField(max_length=255)
    listing_duration = models.CharField(max_length=255)
    description = models.TextField()
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    gross_price = models.DecimalField(decimal_places=10, max_digits=20)
    paypal_email_address = models.CharField(max_length=255, null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)

    country = CountryField()

    publishing_status = models.CharField(max_length=255, choices=EbayItemPublishingStatus.CHOICES,
                                         default=EbayItemPublishingStatus.DRAFT)
    publishing_status_details = jsonfield.JSONField(null=True, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    unpublished_at = models.DateTimeField(null=True, blank=True)

    objects = PassThroughManager.for_queryset_class(EbayItemModelQuerySet)()

    @property
    def ebay_object(self):
        payment_methods = list(self.payment_methods.all().values_list('external_id', flat=True))
        return EbayFixedPriceItem(
            title=self.name,
            description=self.description,
            listing_duration=self.listing_duration,
            country=unicode(self.country),
            postal_code=self.postal_code,
            quantity=self.quantity,
            start_price=self.gross_price,
            paypal_email_address=self.paypal_email_address,
            payment_methods=payment_methods,
            category_id=self.category.external_id,
            shipping_services=[s.ebay_object for s in self.shipping.all()],
            pictures=[i.ebay_object for i in self.images.all()],
            item_specifics=self._build_item_specifics(),
        )

    def _build_item_specifics(self):
        specifics = self.specific_values.all()
        specific_dict = defaultdict(list)
        for specific in specifics:
            specific_dict[specific.specific.name].append(specific.value)

        return [EbayItemSpecific(name=key, values=values) for key, values in specific_dict.iteritems()]

    def set_publishing_status(self, publishing_status, details=None, save=True):
        """
        :type publishing_status: unicode
        :type details:
        :type save: bool
        """
        self.publishing_status = publishing_status
        self.publishing_status_details = details

        if save:
            self.save()


class EbayItemUpdateModel(BaseModel):
    item = models.ForeignKey("products.EbayItemModel", related_name="updates")

    quantity = models.IntegerField(null=True, blank=True)
    gross_price = models.DecimalField(decimal_places=10, max_digits=20,
                                      null=True, blank=True)

    status = models.CharField(max_length=255, choices=EbayItemUpdateStatus.CHOICES,
                              default=EbayItemUpdateStatus.DRAFT)
    status_details = JSONField()

    @property
    def ebay_object(self):
        return EbayReviseFixedPriceItem(
            item_id=self.item.external_id,
            quantity=self.quantity,
            start_price=self.gross_price
        )

    @property
    def has_updated_quantity(self):
        return self.quantity is not None

    @property
    def has_updated_gross_price(self):
        return self.gross_price is not None

    def set_status(self, status, details=None, save=True):
        """
        :type status: unicode
        :type details:
        :type save: bool
        """
        self.status = status
        self.status_details = details

        if save:
            self.save()


class EbayItemSpecificModel(BaseModel):
    item = models.ForeignKey(EbayItemModel, related_name="specific_values")
    specific = models.ForeignKey(CategorySpecificModel, related_name="+")
    value = models.CharField(max_length=255)

    @property
    def ebay_object(self):
        return EbayItemSpecific(self.specific.name, [self.value])


class EbayProductSpecificModel(BaseModel):
    product = models.ForeignKey(EbayProductModel, related_name="specific_values")
    specific = models.ForeignKey(CategorySpecificModel, related_name="+")
    value = models.CharField(max_length=255)


class EbayApiAttemptRequest(BaseModel):
    body = models.TextField()
    headers = JSONField()
    url = models.TextField()
    method = models.TextField()

    @classmethod
    def create_from_ebay_request(cls, request):
        """
        :type request: requests.models.PreparedRequest
        """
        body = EbayParser.make_body_secure(request.body.decode('utf-8'))
        return cls.objects.create(
            body=body,
            headers=dict(request.headers),
            url=request.url,
            method=request.method
        )


class EbayApiAttemptResponse(BaseModel):
    content = models.TextField()
    headers = JSONField()
    url = models.TextField()
    status_code = models.IntegerField()

    @classmethod
    def create_from_response(cls, response):
        """
        :type response: requests.models.Response
        """
        return cls.objects.create(
            content=response.text,
            headers=dict(response.headers),
            url=response.url,
            status_code=response.status_code
        )


class EbayApiAttempt(BaseModel):
    type = models.CharField(max_length=255, choices=EbayApiAttemptType.CHOICES)
    request = models.OneToOneField(EbayApiAttemptRequest, related_name="attempt")
    response = models.OneToOneField(EbayApiAttemptResponse, related_name="attempt")
    success = models.BooleanField(default=False)

    item = models.ForeignKey(EbayItemModel, null=True, blank=True, related_name="attempts")
    item_update = models.ForeignKey(EbayItemUpdateModel, null=True, blank=True, related_name="attempts")

    @classmethod
    def create_from_ebay_exception_for_item_and_type(cls, exception, item, type):
        """
        :type exception: inventorum.ebay.lib.ebay.EbayConnectionException
        :type item: EbayItemModel
        :param type: unicode
        :return: EbayApiAttempt
        """
        return cls.objects.create(
            type=type,
            request=EbayApiAttemptRequest.create_from_ebay_request(exception.response.request),
            response=EbayApiAttemptResponse.create_from_response(exception.response),
            success=False,
            item=item
        )

    @classmethod
    def create_from_service_for_item_and_type(cls, service, item, type):
        """
        Create Model with success true as there was no exception!
        :type service: inventorum.ebay.lib.ebay.items.EbayItems
        :type item: EbayItemModel
        :param type: unicode
        :return: EbayApiAttempt
        """
        return cls.objects.create(
            type=type,
            request=EbayApiAttemptRequest.create_from_ebay_request(service.api.request),
            response=EbayApiAttemptResponse.create_from_response(service.api.response),
            success=True,
            item=item
        )

    @classmethod
    def _create_update_attempt(cls, item_update, request, response, success):
        """
        :type item_update: EbayItemUpdateModel
        :type request: EbayApiAttemptRequest
        :type response: EbayApiAttemptResponse
        :type success: bool
        :rtype: EbayApiAttempt
        """
        return cls.objects.create(
            type=EbayApiAttemptType.UPDATE,
            request=request,
            response=response,
            success=success,
            item=item_update.item,
            item_update=item_update
        )

    @classmethod
    def create_failed_update_attempt(cls, item_update, exception):
        """
        :type item_update: EbayItemUpdateModel
        :type exception: inventorum.ebay.lib.ebay.EbayConnectionException
        :return: EbayApiAttempt
        """
        return cls._create_update_attempt(
            item_update=item_update,
            request=EbayApiAttemptRequest.create_from_ebay_request(exception.response.request),
            response=EbayApiAttemptResponse.create_from_response(exception.response),
            success=False,
        )

    @classmethod
    def create_succeeded_update_attempt(cls, item_update, ebay):
        """
        :type item_update: EbayItemUpdateModel
        :type ebay_api: inventorum.ebay.lib.ebay.Ebay
        :return: EbayApiAttempt
        """
        return cls._create_update_attempt(
            item_update=item_update,
            request=EbayApiAttemptRequest.create_from_ebay_request(ebay.api.request),
            response=EbayApiAttemptResponse.create_from_response(ebay.api.response),
            success=True
        )
