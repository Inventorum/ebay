# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.data import EbayBooleanField, EbayListSerializer
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import IntegerField, ListField, CharField, BooleanField


class EbayListingDuration(object):
    duration_type = None
    duration_id = None

    def __init__(self, duration_type, duration_id):
        self.duration_id = duration_id
        self.duration_type = duration_type


class EbayListingDurationSerializer(POPOSerializer):
    value = IntegerField(source="duration_id")
    _type = CharField(source="duration_type")

    class Meta:
        model = EbayListingDuration
        list_serializer_class = EbayListSerializer


class EbayFeatureDetails(object):
    item_specifics_enabled = None
    durations = None
    category_id = None
    payment_methods = None

    def __init__(self, item_specifics_enabled, durations=None, category_id=None, payment_methods=None):
        self.item_specifics_enabled = item_specifics_enabled
        self.durations = durations
        self.category_id = category_id
        self.payment_methods = payment_methods

    @property
    def durations_dict(self):
        if self.durations is None:
            return None
        return {d.duration_type: d.duration_id for d in self.durations}

    @classmethod
    def create_from_data(cls, data, site_defaults=None):
        """
        Create Ebay feature from data from ebay
        :param data:
        :return: Instance of EbayFeature
        :rtype: EbayFeatureDetails
        :type data: dict
        """
        serializer = EbayFeatureDetailsSerializer(data=data, context={'site_defaults': site_defaults})
        return serializer.build()


class EbayFeatureDetailsSerializer(POPOSerializer):
    CategoryID = CharField(source="category_id", required=False)
    ListingDuration = EbayListingDurationSerializer(many=True, source="durations", required=False)
    PaymentMethod = ListField(child=CharField(), source="payment_methods", required=False)
    ItemSpecificsEnabled = EbayBooleanField(source='item_specifics_enabled')

    class Meta:
        model = EbayFeatureDetails

    def to_internal_value(self, data):
        fields_to_fallback_to_site_defaults = ['ItemSpecificsEnabled', 'PaymentMethod', 'ItemSpecificsEnabled']
        for name in fields_to_fallback_to_site_defaults:
            if name not in data:
                data[name] = self.context['site_defaults'][name]
        return super(EbayFeatureDetailsSerializer, self).to_internal_value(data)


class EbayListingDurationDefinition(object):
    set_id = None
    durations = None

    def __init__(self, set_id, durations=None):
        self.durations = durations
        self.set_id = set_id


class EbayListingDurationDefinitionSerializer(POPOSerializer):
    _durationSetID = IntegerField(source="set_id")
    Duration = ListField(child=CharField(), source="durations")

    class Meta:
        model = EbayListingDurationDefinition
        list_serializer_class = EbayListSerializer


class EbayFeatureDefinition(object):
    durations = None

    def __init__(self, durations=None):
        self.durations = durations

    @property
    def durations_dict(self):
        return {d.set_id: d for d in self.durations}

    @classmethod
    def create_from_data(cls, data):
        """
        Create Ebay feature def from data from ebay
        :param data:
        :return: Instance of EbayFeatureDefinition
        :rtype: EbayFeatureDefinition
        :type data: dict
        """
        serializer = EbayFeatureDefinitionSerializer(data=data)
        return serializer.build()


class EbayFeatureDefinitionSerializer(POPOSerializer):
    ListingDuration = EbayListingDurationDefinitionSerializer(many=True, source="durations", required=False)

    class Meta:
        model = EbayFeatureDefinition


class EbayFeature(object):
    """
    Attributes:
        definition (EbayFeatureDetails): Features details
    """
    definition = None
    details = None
    site_defaults = None

    def get_duration_list_by_type(self, duration_type):
        set_id = self.details.durations_dict[duration_type]
        if set_id is None:
            set_id = self.site_defaults.durations_dict[duration_type]
        return self.definition.durations_dict[set_id].durations

    @property
    def payment_methods(self):
        if self.details.payment_methods is None:
            return self.site_defaults.payment_methods
        return self.details.payment_methods

    @classmethod
    def create_from_data(cls, data):
        """
        Create Ebay feature from data from ebay
        :param data:
        :return: Instance of EbaySiteDefaults
        :rtype: EbaySiteDefaults
        :type data: dict
        """
        instance = cls()
        durations = data['FeatureDefinitions']['ListingDurations']
        instance.definition = EbayFeatureDefinition.create_from_data(durations)

        details_data = data.get('Category', data.get('SiteDefaults'))
        instance.details = EbayFeatureDetails.create_from_data(details_data, data.get('SiteDefaults'))
        instance.site_defaults = EbayFeatureDetails.create_from_data(data.get('SiteDefaults'))
        return instance