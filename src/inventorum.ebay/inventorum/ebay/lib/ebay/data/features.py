# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import IntegerField, ListField, CharField


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


class EbayFeatureDetails(object):
    durations = None
    category_id = None

    def __init__(self, durations=None, category_id=None):
        self.durations = durations or []
        self.category_id = category_id

    @property
    def durations_dict(self):
        return {d.duration_type: d.duration_id for d in self.durations}

    @classmethod
    def create_from_data(cls, data):
        """
        Create Ebay feature from data from ebay
        :param data:
        :return: Instance of EbayFeature
        :rtype: EbayFeatureDetails
        :type data: dict
        """
        serializer = EbayFeatureDetailsSerializer(data=data)
        return serializer.build()


class EbayFeatureDetailsSerializer(POPOSerializer):
    CategoryID = CharField(source="category_id", required=False)
    ListingDuration = EbayListingDurationSerializer(many=True, source="durations", required=False)

    class Meta:
        model = EbayFeatureDetails


class EbayListingDurationDefinition(object):
    set_id = None
    durations = None

    def __init__(self, set_id, durations=None):
        self.durations = durations or []
        self.set_id = set_id


class EbayListingDurationDefinitionSerializer(POPOSerializer):
    _durationSetID = IntegerField(source="set_id")
    Duration = ListField(child=CharField(), source="durations")

    class Meta:
        model = EbayListingDurationDefinition


class EbayFeatureDefinition(object):
    durations = None

    def __init__(self, durations=None):
        self.durations = durations or []

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
        feature_definition (EbayFeatureDetails): Features details
    """
    definition = None
    details = None

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
        instance.details = EbayFeatureDetails.create_from_data(details_data)
        return instance