# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django_countries.fields import CountryField
from inventorum.ebay.lib.db.models import BaseModel, BaseQuerySet

from django.db.models import fields
from inventorum.util.django.model_utils import PassThroughManager

log = logging.getLogger(__name__)


class ShippingServiceQuerySet(BaseQuerySet):

    def by_country(self, country_code):
        return self.filter(country=country_code)


class ShippingServiceModel(BaseModel):
    country = CountryField()

    external_id = fields.CharField(max_length=255)
    description = fields.CharField(max_length=512)

    shipping_time_min = fields.IntegerField(null=True, blank=True)
    shipping_time_max = fields.IntegerField(null=True, blank=True)

    is_international = fields.BooleanField(default=False)

    objects = PassThroughManager.for_queryset_class(ShippingServiceQuerySet)()

    @classmethod
    def create_or_update_from_ebay_shipping_service(cls, ebay_shipping_service, country_code):
        """
        :type ebay_shipping_service: inventorum.ebay.lib.ebay.details.EbayShippingService
        :type country_code: unicode
        :rtype: ShippingServiceModel
        """
        attributes = dict(
            description=ebay_shipping_service.description,
            shipping_time_min=ebay_shipping_service.shipping_time_min,
            shipping_time_max=ebay_shipping_service.shipping_time_max,
            is_international=ebay_shipping_service.international
        )

        shipping_service, created = cls.objects.get_or_create(
            external_id=ebay_shipping_service.id,
            country=country_code,
            defaults=attributes
        )

        update = not created
        if update:
            for key, value in attributes.iteritems():
                setattr(shipping_service, key, value)

            shipping_service.save()

        return shipping_service
