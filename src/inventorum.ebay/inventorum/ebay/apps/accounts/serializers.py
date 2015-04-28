# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.utils.translation import ugettext
from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.ebay.apps.shipping.serializers import ShippingServiceConfigurableSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


class EbayAccountSerializer(ShippingServiceConfigurableSerializer, serializers.ModelSerializer):

    class Meta:
        model = EbayAccountModel
        fields = ('shipping_services', )

    def validate_shipping_services(self, shipping_services):
        """
        Validates the correct country scope of the shipping services

        :type shipping_services: list[dict]
        """
        account = self.instance
        for config in shipping_services:
            if config["service"].country != account.country:
                raise ValidationError(ugettext("Invalid shipping service"))
        return shipping_services

    def update(self, instance, validated_data):
        """
        :type instance: EbayAccountModel
        :type validated_data: dict
        """
        self.create_or_update_shipping_services(instance, validated_data)
        return super(EbayAccountSerializer, self).update(instance, validated_data)
