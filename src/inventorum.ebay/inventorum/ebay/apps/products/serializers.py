# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext

from inventorum.ebay.apps.categories.models import CategoryModel

from inventorum.ebay.apps.categories.serializers import CategorySerializer, CategoryBreadcrumbSerializer, \
    CategorySpecificsSerializer
from inventorum.ebay.apps.products.models import EbayProductModel, EbayProductSpecificModel
from inventorum.ebay.lib.rest.fields import RelatedModelByIdField
from rest_framework import serializers


log = logging.getLogger(__name__)


class EbayProductSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayProductSpecificModel
        fields = ('specific', 'value')


class EbayProductCategorySerializer(CategorySerializer):

    class Meta:
        model = CategoryModel
        fields = CategorySerializer.Meta.fields + ("breadcrumb", "specifics")

    breadcrumb = CategoryBreadcrumbSerializer(source="ancestors", many=True)
    specifics = CategorySpecificsSerializer(many=True)


class EbayProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = EbayProductModel
        fields = ('id', 'category', 'is_published', 'listing_url', 'specific_values')

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



    def update(self, instance, validated_data):
        self._update_specific_values(instance, validated_data)
        return super(EbayProductSerializer, self).update(instance, validated_data)

    def _update_specific_values(self, instance, validated_data):
        specific_values = validated_data.pop('specific_values', None)
        if not specific_values:
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
                prod_spec_obj.__dict__.update(defaults)
                prod_spec_obj.save()
            new_specific_values.append(prod_spec_obj.id)

        to_be_deleted = current_specific_values - set(new_specific_values)
        if to_be_deleted:
            instance.specific_values.filter(id__in=to_be_deleted).delete()


