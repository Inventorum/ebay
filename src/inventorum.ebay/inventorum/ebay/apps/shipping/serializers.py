# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel, ShippingServiceModel

from rest_framework import serializers


log = logging.getLogger(__name__)


class ShippingServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingServiceModel
        fields = ('id', 'external_id', 'description', 'shipping_time_min', 'shipping_time_max', 'is_international')


class ShippingServiceConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingServiceConfigurationModel
        fields = ('service', 'cost', 'additional_cost')

    # service = serializers.PrimaryKeyRelatedField(queryset=ShippingServiceModel.objects.all())
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    additional_cost = serializers.DecimalField(max_digits=10, decimal_places=2)


class ShippingServiceConfigurableSerializer(serializers.Serializer):
    """ Mixin for serializers for entities that can be configured with shipping services """

    shipping_services = ShippingServiceConfigurationSerializer(many=True)

    def create_or_update_shipping_services(self, entity, validated_data):
        """
        :type entity: inventorum.ebay.apps.shipping.models.ShippingServiceConfigurable
        :type validated_data: dict

        :rtype: dict
        """
        if "shipping_services" not in validated_data:
            return

        shipping_services = validated_data.pop("shipping_services")

        created_or_updated_ids = []
        for data in shipping_services:
            service_config, created = entity.shipping_services.get_or_create(service=data["service"], defaults=data)
            if not created:
                for key, value in data.iteritems():
                    setattr(service_config, key, value)
                service_config.save()
            created_or_updated_ids.append(service_config.id)

        # remove those that were not created or updated
        entity.shipping_services.exclude(id__in=created_or_updated_ids).delete()
