# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging

from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.lib.rest.fields import MoneyField
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

    def __init__(self, id, name, gross_price, tax_type_id, quantity, images, variation_count=0, variations=None,
                 attributes=None, description=None):
        """
        :type id: int
        :type name: unicode
        :type gross_price: decimal.Decimal
        :type tax_type_id: int
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
        self.tax_type_id = tax_type_id
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
        gross_price = MoneyField()

        images = CoreProductImageDeserializer(many=True)

    class Meta(POPOSerializer.Meta):
        model = CoreProduct

    id = serializers.IntegerField()
    name = serializers.CharField()
    gross_price = MoneyField()
    tax_type = serializers.IntegerField(source="tax_type_id")
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

    # Serializer #########################

    class Serializer(POPOSerializer):

        class Meta(POPOSerializer.Meta):
            model = None

        id = serializers.IntegerField()
        address1 = serializers.CharField()
        address2 = serializers.CharField(allow_null=True, required=False, allow_blank=True)
        zipcode = serializers.CharField()
        city = serializers.CharField()
        state = serializers.CharField(allow_null=True, required=False, allow_blank=True)
        country = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        company = serializers.CharField(allow_null=True, required=False, allow_blank=True)

    # / Serializer #######################

    def __init__(self, id, address1, zipcode, city, country, first_name, last_name, address2="", company="", state=""):
        """
        :type id: int
        :type address1: unicode
        :type address2: unicode
        :type zipcode: unicode
        :type city: unicode
        :type country: unicode
        :type first_name: unicode
        :type last_name: unicode
        :type company: unicode
        :type state: unicode
        """
        self.id = id
        self.address1 = address1
        self.address2 = address2
        self.zipcode = zipcode
        self.city = city
        self.country = country
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.state = state

CoreAddress.Serializer.Meta.model = CoreAddress


class CoreAccountSettings(object):

    def __init__(self, ebay_click_and_collect=False):
        """
        :type ebay_click_and_collect: boolean
        """
        self.ebay_click_and_collect = ebay_click_and_collect


class CoreAccountSettingsDeserializer(POPOSerializer):
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
    billing_address = CoreAddress.Serializer(required=False, allow_null=True)
    opening_hours = CoreOpeningHours.Deserializer(required=False, many=True)

    class Meta(POPOSerializer.Meta):
        model = CoreAccount


class CoreInfo(object):
    def __init__(self, account, tax_types):
        """
        :type account: CoreAccount
        :type tax_types: list[CoreTaxType]
        """
        self.account = account
        self.tax_types = tax_types

    def get_tax_rate_for(self, tax_type_id):
        """
        :type tax_type_id: int
        """
        return next((tax_type.tax_rate for tax_type in self.tax_types if tax_type.id == tax_type_id), None)


class CoreTaxType(object):

    class Serializer(POPOSerializer):

        class Meta:
            model = None

        id = serializers.IntegerField()
        tax_rate = serializers.DecimalField(max_digits=13, decimal_places=10)

    def __init__(self, id, tax_rate):
        """
        :type id: int
        :type tax_rate: decimal.Decimal
        """
        self.id = id
        self.tax_rate = tax_rate.quantize(Decimal("0.000"))

CoreTaxType.Serializer.Meta.model = CoreTaxType


class CoreInfoDeserializer(POPOSerializer):
    account = CoreAccountDeserializer()
    tax_types = CoreTaxType.Serializer(many=True)

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
        gross_price = MoneyField()

    class Meta(POPOSerializer.Meta):
        model = CoreProductDelta

    id = serializers.IntegerField()
    parent = serializers.IntegerField(allow_null=True, required=False)
    name = serializers.CharField()
    state = serializers.CharField()
    gross_price = MoneyField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    # meta will be removed after meta overwrites
    meta = serializers.DictField(required=False, child=MetaDeserializer())

    def create(self, validated_data):
        self.overwrite_attrs_from_meta(validated_data, remove_meta=True)
        return super(CoreProductDeltaDeserializer, self).create(validated_data)


class CoreBasketItem(object):

    # Serializer #########################

    class Serializer(POPOSerializer):

        class Meta(POPOSerializer.Meta):
            model = None

        id = serializers.IntegerField()
        name = serializers.CharField()
        quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    # / Serializer #######################

    def __init__(self, id, name, quantity):
        """
        :type id: int
        :type name: unicode
        :type quantity: decimal.Decimal
        """
        self.id = id
        self.name = name
        self.quantity = quantity

CoreBasketItem.Serializer.Meta.model = CoreBasketItem


class CoreBasket(object):

    # Serializer #########################

    class Serializer(POPOSerializer):

        class Meta(POPOSerializer.Meta):
            model = None

        items = CoreBasketItem.Serializer(many=True)

    # / Serializer #######################

    def __init__(self, items):
        """
        :type items: list[CoreBasketItem]
        """
        self.items = items

CoreBasket.Serializer.Meta.model = CoreBasket


class CoreOrder(object):

    # Serializer #########################

    class Serializer(POPOSerializer):

        class Meta(POPOSerializer.Meta):
            model = None

        id = serializers.IntegerField()
        state = serializers.IntegerField()

        basket = CoreBasket.Serializer()

    # / Serializer #######################

    def __init__(self, id, state, basket):
        """
        :type id: int
        :type state: int
        :type basket: CoreBasket
        """
        self.id = id
        self.state = state
        self.basket = basket

    @property
    def is_paid(self):
        return self.state & BinaryCoreOrderStates.PAID == BinaryCoreOrderStates.PAID

    @property
    def is_shipped(self):
        return self.state & BinaryCoreOrderStates.SHIPPED == BinaryCoreOrderStates.SHIPPED

    @property
    def is_delivered(self):
        return self.state & BinaryCoreOrderStates.DELIVERED == BinaryCoreOrderStates.DELIVERED

    @property
    def is_closed(self):
        return self.state & BinaryCoreOrderStates.CLOSED == BinaryCoreOrderStates.CLOSED

    @property
    def is_canceled(self):
        return self.state & BinaryCoreOrderStates.CANCELED == BinaryCoreOrderStates.CANCELED

CoreOrder.Serializer.Meta.model = CoreOrder


class CoreDeltaReturnItem(object):

    # Serializer #########################

    class Serializer(POPOSerializer):

        class Meta(POPOSerializer.Meta):
            model = None

        id = serializers.IntegerField()
        basket_item = serializers.IntegerField(source="basket_item_id")
        name = serializers.CharField()
        quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
        amount = MoneyField()

    # / Serializer #######################

    def __init__(self, id, basket_item_id, name, quantity, amount):
        """
        :type id: int
        :type basket_item_id: int
        :type name: unicode
        :type quantity: decimal.Decimal
        :type amount: decimal.Decimal
        """
        self.id = id
        self.basket_item_id = basket_item_id
        self.name = name
        self.quantity = quantity
        self.amount = amount

CoreDeltaReturnItem.Serializer.Meta.model = CoreDeltaReturnItem


class CoreDeltaReturn(object):

    # Serializer #########################

    class Serializer(POPOSerializer):

        class Meta(POPOSerializer.Meta):
            model = None

        id = serializers.IntegerField()
        order = serializers.IntegerField(source="order_id")
        total_amount = MoneyField()
        items = CoreDeltaReturnItem.Serializer(many=True)

    # / Serializer #######################

    def __init__(self, id, order_id, total_amount, items):
        """
        :type id: int
        :type order_id: int
        :type total_amount: decimal.Decimal
        :type items: list[CoreDeltaReturnItem]
        """
        self.id = id
        self.order_id = order_id
        self.total_amount = total_amount
        self.items = items

CoreDeltaReturn.Serializer.Meta.model = CoreDeltaReturn
