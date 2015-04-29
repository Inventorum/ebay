# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_countries.fields import CountryField
from inventorum.ebay.lib.db.models import BaseModel, BaseQuerySet

from inventorum.util.django.model_utils import PassThroughManager

log = logging.getLogger(__name__)


class ShippingServiceQuerySet(BaseQuerySet):

    def by_country(self, country_code):
        return self.filter(country=country_code)


class ShippingServiceModel(BaseModel):
    """
    Persistent representation of an ebay shipping service.

    While a shipping service is not directly associated with shipping costs, it can be configured
    for various purposes through the ``ShippingServiceConfigurationModel``.
    """
    country = CountryField()

    external_id = models.CharField(max_length=255)
    description = models.CharField(max_length=512)

    shipping_time_min = models.IntegerField(null=True, blank=True)
    shipping_time_max = models.IntegerField(null=True, blank=True)

    is_international = models.BooleanField(default=False)

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


class ShippingServiceConfigurationModel(BaseModel):
    """
    This model represents a selection or configuration of an ebay shipping service with associated shipping costs.

    Apart from the generic entity relation, which allows to assign many shipping service configurations to a
    ShippingServiceConfigurable model (either ``EbayAccountModel`` or ``EbayProductModel``), this model can
    also represent a selected shipping service configuration in an ``OrderModel``.
    """
    service = models.ForeignKey("shipping.ShippingServiceModel")

    # Note: In case the instance is assigned as shipping to an order, the cost always represent the total shipping cost
    # and there are no additional costs
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2, default=D("0.00"))

    # Generic relationship to a "shipping configurable" entity that can have *many* shipping service configurations
    entity_type = models.ForeignKey(ContentType, blank=True, null=True)
    entity_id = models.PositiveIntegerField(blank=True, null=True)
    entity = GenericForeignKey("entity_type", "entity_id")

    def is_free_shipping(self):
        return self.cost + self.additional_cost == 0


class ShippingServiceConfigurable(models.Model):
    """
    Mixin for models that can be configured with multiple shipping services (EbayAccountModel and EbayProductModel)

    Note jm: We've to inherit here form models, otherwise django won't pick up the generic field.
    See: http://stackoverflow.com/questions/28115239/django-genericrelation-in-model-mixin
    """
    class Meta:
        abstract = True

    shipping_services = GenericRelation("shipping.ShippingServiceConfigurationModel",
                                        content_type_field="entity_type",
                                        object_id_field="entity_id")
