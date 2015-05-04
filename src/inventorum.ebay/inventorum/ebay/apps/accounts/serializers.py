# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.utils.translation import ugettext
from inventorum.ebay.apps.accounts.models import EbayAccountModel, EbayLocationModel, AddressModel
from inventorum.ebay.apps.shipping.serializers import ShippingServiceConfigurableSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressModel
        fields = ('name', 'street', 'street1', 'city', 'country', 'postal_code', 'region')


class EbayLocationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = EbayLocationModel
        fields = ('address', 'latitude', 'longitude', 'name', 'phone', 'pickup_instruction', 'url')

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        self.create_or_update_address(instance, address_data)
        return super(EbayLocationSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        instance = super(EbayLocationSerializer, self).create(validated_data)
        self.create_or_update_address(instance, address_data)
        return instance

    def create_or_update_address(self, instance, address_data):
        if not address_data:
            raise serializers.ValidationError('Missing `address` in location')

        serializer = AddressSerializer(instance=instance.address, data=address_data)
        serializer.is_valid(raise_exception=True)
        address_object = serializer.save()

        instance.address = address_object
        instance.save()


class EbayAccountSerializer(ShippingServiceConfigurableSerializer, serializers.ModelSerializer):
    location = EbayLocationSerializer(required=False, allow_null=True)

    class Meta:
        model = EbayAccountModel
        read_only_fields = ('email', 'user_id')
        fields = ('shipping_services', 'location') + read_only_fields

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
        self.create_or_update_location(instance, validated_data)
        return super(EbayAccountSerializer, self).update(instance, validated_data)

    def create_or_update_location(self, instance, validated_data):
        location = validated_data.pop('location', None)
        if not location:
            EbayLocationModel.objects.filter(account=instance).delete()
            return

        if not hasattr(instance, 'location'):
            location_instance = None
        else:
            location_instance = instance.location

        serializer = EbayLocationSerializer(instance=location_instance, data=location)
        serializer.is_valid(raise_exception=True)
        location_instance = serializer.save()
        location_instance.account = instance
        location_instance.save()