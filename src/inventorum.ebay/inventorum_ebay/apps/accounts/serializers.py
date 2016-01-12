# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.utils.translation import ugettext
from inventorum_ebay.apps.accounts.models import EbayAccountModel, EbayLocationModel, AddressModel, ReturnPolicyModel
from inventorum_ebay.apps.returns import ReturnsAcceptedOption, ReturnsWithinOption, ShippingCostPaidByOption
from inventorum_ebay.apps.shipping.serializers import ShippingServiceConfigurableSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


class AddressSerializer(serializers.ModelSerializer):
    country = serializers.CharField()

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


class ReturnPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnPolicyModel
        fields = ('returns_accepted_option', 'returns_within_option', 'shipping_cost_paid_by_option', 'description')

    returns_accepted_option = serializers.ChoiceField(required=False, choices=ReturnsAcceptedOption.CHOICES)
    returns_within_option = serializers.ChoiceField(required=False, allow_null=True, choices=ReturnsWithinOption.CHOICES)
    shipping_cost_paid_by_option = serializers.ChoiceField(required=False, allow_null=True,
                                                           choices=ShippingCostPaidByOption.CHOICES)
    description = serializers.CharField(max_length=5000, allow_null=True, required=False)


class EbayAccountSerializer(ShippingServiceConfigurableSerializer, serializers.ModelSerializer):
    location = EbayLocationSerializer(required=False, allow_null=True)
    return_policy = ReturnPolicySerializer(required=False, allow_null=True)

    class Meta:
        model = EbayAccountModel
        read_only_fields = ('email', 'user_id')
        fields = ('shipping_services', 'location', 'return_policy', 'payment_method_paypal_enabled',
                  'payment_method_paypal_email_address', 'payment_method_bank_transfer_enabled') + read_only_fields

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
        self.create_or_update_return_policy(instance, validated_data)

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

    def create_or_update_return_policy(self, instance, validated_data):
        return_policy_data = validated_data.pop('return_policy', None)

        if not return_policy_data:
            return

        if not instance.has_return_policy:
            # create a new return policy
            instance.return_policy = ReturnPolicyModel.create(**return_policy_data)
            instance.save()
        else:
            # update the existing return policy
            ReturnPolicyModel.objects.filter(id=instance.return_policy.id)\
                .update(**return_policy_data)
