# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext

from inventorum.ebay.apps.categories.models import CategoryModel

from inventorum.ebay.apps.categories.serializers import CategorySerializer, CategoryBreadcrumbSerializer, \
    CategorySpecificsSerializer
from inventorum.ebay.apps.products.models import EbayProductModel, EbayProductSpecificModel
from inventorum.ebay.apps.shipping.serializers import ShippingServiceConfigurableSerializer
from inventorum.ebay.lib.rest.fields import RelatedModelByIdField
from rest_framework import serializers


log = logging.getLogger(__name__)


class EbayProductSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayProductSpecificModel
        fields = ('specific', 'value')

    def validate(self, attrs):
        self._validate_value(attrs['specific'], attrs['value'])
        return attrs

    def _validate_value(self, specific, value):
        if specific.can_use_own_values:
            return

        values = specific.values.all().values_list('value', flat=True)
        if value not in values:
            raise ValidationError(ugettext('This item specific does not accept custom values (wrong: `%(value)s`)')
                                  % {'value': value})


class EbayProductCategorySerializer(CategorySerializer):
    class Meta:
        model = CategoryModel
        fields = CategorySerializer.Meta.fields + ("breadcrumb", "specifics")

    breadcrumb = CategoryBreadcrumbSerializer(source="ancestors", many=True)
    specifics = CategorySpecificsSerializer(many=True)


class EbayProductSerializer(ShippingServiceConfigurableSerializer, serializers.ModelSerializer):

    class Meta:
        model = EbayProductModel
        fields = ('id', 'category', 'is_published', 'listing_url', 'specific_values', 'shipping_services')

    category = RelatedModelByIdField(serializer=EbayProductCategorySerializer, allow_null=True, required=False)

    is_published = serializers.BooleanField(read_only=True)
    listing_url = serializers.BooleanField(read_only=True)
    specific_values = EbayProductSpecificSerializer(many=True)

    def validate_category(self, category):
        if category is None:
            return None

        if not category.is_leaf:
            raise ValidationError(ugettext("Given category is not a leaf"))

        product = self.instance
        if category.country != product.account.country:
            raise ValidationError(ugettext("Invalid category"))

        return category

    def validate_shipping_services(self, shipping_services):
        """
        Validates the correct country scope of the shipping services

        :type shipping_services: list[dict]
        """
        product = self.instance
        for config in shipping_services:
            if config["service"].country != product.account.country:
                raise ValidationError(ugettext("Invalid category"))
        return shipping_services

    def validate(self, attrs):
        specific_values = attrs.get('specific_values', None)
        category = attrs.get('category', None)
        if specific_values and category:
            self._validate_specific_values_categories_are_correct(specific_values, category)
            self._validate_specific_values_if_min_values_are_ok(specific_values, category)
            self._validate_specific_values_if_max_values_are_ok(specific_values, category)
        return attrs

    def _validate_specific_values_if_min_values_are_ok(self, specific_values, category):
        specific_values_ids_count = defaultdict(lambda: 0)
        for sv in specific_values:
            specific_values_ids_count[sv['specific'].pk] += 1

        required_ones = dict(category.specifics.required().values_list('id', 'min_values'))

        missing_ids = []
        for specific_id, min_value in required_ones.iteritems():
            send_value = specific_values_ids_count.get(specific_id, None)
            if not send_value or send_value < min_value:
                missing_ids.append(specific_id)

        if missing_ids:
            raise ValidationError(ugettext('You need to pass all required specifics (missing: %(missing_ids)s)!')
                                  % {'missing_ids': list(missing_ids)})

        return specific_values

    def _validate_specific_values_if_max_values_are_ok(self, specific_values, category):
        specific_values_ids_count = defaultdict(lambda: 0)
        for sv in specific_values:
            specific_values_ids_count[sv['specific'].pk] += 1

        max_values = dict(category.specifics.required().values_list('id', 'max_values'))

        too_many_values_ids = []
        for specific_id, max_value in max_values.iteritems():
            send_value = specific_values_ids_count.get(specific_id, None)
            if send_value and send_value > max_value:
                too_many_values_ids.append(specific_id)

        if too_many_values_ids:
            raise ValidationError(ugettext('You send too many values for one specific '
                                           '(specific_ids: %(too_many_values_ids)s)!')
                                  % {'too_many_values_ids': list(too_many_values_ids)})

        return specific_values

    def _validate_specific_values_categories_are_correct(self, specific_values, category):
        wrong_ids = [sv['specific'].id for sv in specific_values
                     if sv['specific'].category_id != category.id]

        if wrong_ids:
            raise ValidationError(ugettext('Some specifics are assigned to different category than product! '
                                           '(wrong specific ids: %(wrong_ids)s)') % {'wrong_ids': wrong_ids})

    def update(self, instance, validated_data):
        self.create_or_update_specific_values(instance, validated_data)
        self.create_or_update_shipping_services(instance, validated_data)
        return super(EbayProductSerializer, self).update(instance, validated_data)

    def create_or_update_specific_values(self, instance, validated_data):
        specific_values = validated_data.pop('specific_values', None)
        if specific_values is None:
            return

        current_specific_values = set(instance.specific_values.values_list('id', flat=True))
        new_specific_values = []
        for val in specific_values:
            specific_obj = val['specific']
            value = val['value']
            defaults = dict(value=value)
            prod_spec_obj, c = EbayProductSpecificModel.objects.get_or_create(
                specific=specific_obj,
                product=instance,
                defaults=defaults
            )
            if not c:
                for key, value in defaults.iteritems():
                    setattr(prod_spec_obj, key, value)
                prod_spec_obj.save()
            new_specific_values.append(prod_spec_obj.id)

        to_be_deleted = current_specific_values - set(new_specific_values)
        if to_be_deleted:
            instance.specific_values.filter(id__in=to_be_deleted).delete()
