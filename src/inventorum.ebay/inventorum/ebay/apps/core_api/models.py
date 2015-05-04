# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework import serializers

from inventorum.ebay.lib.rest.serializers import POPOSerializer


log = logging.getLogger(__name__)


class CoreProductMetaOverrideMixin(object):
    def overwrite_attrs_from_meta(self, validated_data, remove_meta=True):
        """
        Overwrites channeled core product attributes from ebay meta in the given validated data
        and removes the meta information afterwards.

        If `remove_meta` is True, the meta information will be removed from the validated data afterwards.

        :type validated_data: dict
        :type remove_meta: bool
        """
        if "meta" in validated_data:
            if "ebay" in validated_data["meta"]:
                ebay_meta = validated_data["meta"]["ebay"]

                def overwrite_from_meta(attr):
                    if attr in ebay_meta and ebay_meta[attr]:
                        validated_data[attr] = ebay_meta[attr]

                overwrite_from_meta("name")
                overwrite_from_meta("description")
                overwrite_from_meta("gross_price")

                overwrite_from_meta("images")

            if remove_meta:
                # we need meta only for attr overwrites => throw it away afterwards
                del validated_data["meta"]


class CoreProduct(object):
    """ Represents a core product from the inventorum api """

    def __init__(self, id, name, gross_price, quantity, images, variation_count=0, variations=None,
                 attributes=None, description=None):
        """
        :type id: int
        :type name: unicode
        :type gross_price: decimal.Decimal
        :type quantity: decimal.Decimal
        :type images: list of CoreProductImage
        :type variation_count: int
        :type variations: list[CoreProduct] | None
        :type attributes: list[CoreProductAttribute] | None
        :type description: unicode | None
        """
        self.id = id
        self.name = name
        self.gross_price = gross_price
        self.quantity = quantity
        self.images = images
        self.variation_count = variation_count
        self.variations = variations or []
        self.attributes = attributes
        self.description = description

    @property
    def is_parent(self):
        return len(self.variations) > 0


class CoreProductImage(object):
    """ Represents a product image embedded in a core product"""

    def __init__(self, id, url):
        """
        :type id: int
        :type url: unicode
        """
        self.id = id
        self.url = url


class CoreProductImageDeserializer(POPOSerializer):
    class Meta:
        model = CoreProductImage

    id = serializers.IntegerField()
    ipad_retina = serializers.CharField(source="url")


class CoreProductAttribute(object):
    def __init__(self, key, values):
        self.key = key
        self.values = values


class CoreProductAttributeListSerializer(serializers.ListSerializer):
    def to_internal_value(self, data):
        new_data = []
        if isinstance(data, dict):
            for key, value in data.iteritems():
                new_data.append({
                    'key': key,
                    'values': value
                })
        else:
            raise serializers.ValidationError('In `attributes` got something that is not dict: %s' % data)
        return super(CoreProductAttributeListSerializer, self).to_internal_value(new_data)


class CoreProductAttributeSerializer(POPOSerializer):
    key = serializers.CharField()
    values = serializers.ListField(child=serializers.CharField())

    class Meta(POPOSerializer.Meta):
        model = CoreProductAttribute
        list_serializer_class = CoreProductAttributeListSerializer


class CoreBasicProductDeserializer(POPOSerializer, CoreProductMetaOverrideMixin):

    class MetaDeserializer(serializers.Serializer):
        """ Helper deserializer for nested meta information (won't be assigned to POPOs) """
        name = serializers.CharField(allow_null=True, allow_blank=True)
        description = serializers.CharField(allow_null=True, allow_blank=True)
        gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)

        images = CoreProductImageDeserializer(many=True)

    class Meta(POPOSerializer.Meta):
        model = CoreProduct

    id = serializers.IntegerField()
    name = serializers.CharField()
    gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    images = CoreProductImageDeserializer(many=True)
    attributes = CoreProductAttributeSerializer(many=True)

    # meta will be removed after meta overwrites
    meta = serializers.DictField(child=MetaDeserializer())

    def create(self, validated_data):
        self.overwrite_attrs_from_meta(validated_data, remove_meta=True)
        return super(CoreBasicProductDeserializer, self).create(validated_data)


class CoreProductDeserializer(CoreBasicProductDeserializer):
    variations = CoreBasicProductDeserializer(many=True, required=False)
    variation_count = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)


class CoreAddress(object):
    def __init__(self, id, address1, address2, zipcode, city, country, first_name, last_name, company, state=""):
        """
        :type id: int
        :type address1: unicode
        :type address2: unicode
        :type zipcode: unicode
        :type city: unicode
        :type state: unicode
        :type country: unicode
        :type first_name: unicode
        :type last_name: unicode
        :type company: unicode
        """
        self.id = id
        self.address1 = address1
        self.address2 = address2
        self.zipcode = zipcode
        self.city = city
        self.state = state
        self.country = country
        self.first_name = first_name
        self.last_name = last_name
        self.company = company


class CoreAddressDeserializer(POPOSerializer):
    id = serializers.IntegerField()
    address1 = serializers.CharField()
    address2 = serializers.CharField(allow_null=True)
    zipcode = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    country = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    company = serializers.CharField(allow_null=True)

    class Meta(POPOSerializer.Meta):
        model = CoreAddress


class CoreAccountSettings(object):
    EBAY_PAYMENTS_MAPPING = {
        1: 'PayPal',
        2: 'MoneyXferAccepted'
    }

    def __init__(self, ebay_paypal_email, ebay_payment_methods, ebay_click_and_collect=False):
        """
        :type shipping_services: list of CoreShippingService
        :type ebay_paypal_email: unicode
        :type ebay_click_and_collect: boolean
        :type ebay_payment_methods: list[unicode]
        """
        self.ebay_paypal_email = ebay_paypal_email
        self.ebay_click_and_collect = ebay_click_and_collect
        self.ebay_payment_methods = [self.EBAY_PAYMENTS_MAPPING[m] for m in ebay_payment_methods]


class CoreAccountSettingsDeserializer(POPOSerializer):
    ebay_paypal_email = serializers.CharField(allow_null=True)
    ebay_payment_methods = serializers.ListField(child=serializers.IntegerField(), allow_null=True)
    ebay_click_and_collect = serializers.BooleanField(default=False, required=False)

    class Meta(POPOSerializer.Meta):
        model = CoreAccountSettings


class CoreOpeningHours(object):
    class Deserializer(POPOSerializer):
        class Meta:
            model = None

        closes_hour = serializers.IntegerField()
        closes_minute = serializers.IntegerField()
        day_of_week = serializers.IntegerField()
        opens_hour = serializers.IntegerField()
        opens_minute = serializers.IntegerField()
        enabled = serializers.BooleanField()

    def __init__(self, closes_hour, closes_minute, day_of_week, opens_hour, opens_minute, enabled=False):
        self.closes_hour = closes_hour
        self.closes_minute = closes_minute
        self.day_of_week = day_of_week
        self.opens_hour = opens_hour
        self.opens_minute = opens_minute
        self.enabled = enabled

CoreOpeningHours.Deserializer.Meta.model = CoreOpeningHours


class CoreAccount(object):
    def __init__(self, country, settings, email=None, billing_address=None, opening_hours=None):
        """
        :type settings: CoreAccountSettings
        :type email: unicode | None
        :type billing_address: CoreAddress
        :type opening_hours: list[CoreOpeningHours]
        """
        self.email = email
        self.country = country
        self.billing_address = billing_address
        self.settings = settings
        self.opening_hours = [o for o in opening_hours or [] if o.enabled]


class CoreAccountDeserializer(POPOSerializer):
    email = serializers.EmailField()
    country = serializers.CharField()
    settings = CoreAccountSettingsDeserializer()
    billing_address = CoreAddressDeserializer(required=False)
    opening_hours = CoreOpeningHours.Deserializer(required=False, many=True)

    class Meta(POPOSerializer.Meta):
        model = CoreAccount


class CoreInfo(object):
    def __init__(self, account):
        self.account = account


class CoreInfoDeserializer(POPOSerializer):
    account = CoreAccountDeserializer()

    class Meta:
        model = CoreInfo


class CoreProductDelta(object):
    def __init__(self, id, name, state, gross_price, quantity, parent=None):
        """
        :type id: int
        :type id: unicode
        :type state: unicode
        :type gross_price: decimal.Decimal
        :type quantity: decimal.Decimal
        """
        self.id = id
        self.name = name
        self.state = state
        self.gross_price = gross_price
        self.quantity = quantity
        self.parent = parent


class CoreProductDeltaDeserializer(POPOSerializer, CoreProductMetaOverrideMixin):

    class MetaDeserializer(serializers.Serializer):
        """ Helper deserializer for nested meta information (won't be assigned to POPOs) """
        gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta(POPOSerializer.Meta):
        model = CoreProductDelta

    id = serializers.IntegerField()
    parent = serializers.IntegerField(allow_null=True, required=False)
    name = serializers.CharField()
    state = serializers.CharField()
    gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    # meta will be removed after meta overwrites
    meta = serializers.DictField(required=False, child=MetaDeserializer())

    def create(self, validated_data):
        self.overwrite_attrs_from_meta(validated_data, remove_meta=True)
        return super(CoreProductDeltaDeserializer, self).create(validated_data)


