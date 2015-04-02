# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework import serializers


log = logging.getLogger(__name__)


class POPOSerializer(serializers.Serializer):
    """
    Serializer for Plain Old Python Objects (POPO)
    """

    def create(self, validated_data):
        """
        :type validated_data: dict | collections.OrderedDict
        """
        assert hasattr(self, "Meta") and hasattr(self.Meta, "model"), "No `Meta.model` defined"

        ModelClass = self.Meta.model

        for original_name, field in self.fields.iteritems():
            name = field.source
            if name in validated_data:
                if isinstance(field, POPOSerializer) and name in validated_data:
                    # Note: We call create directly since the data has already been validated
                    validated_data[name] = field.create(validated_data[name])
                elif isinstance(field, serializers.ListSerializer) and isinstance(field.child, POPOSerializer):
                    validated_data[name] = [field.child.create(validated_item) for validated_item in validated_data[name]]

        return ModelClass(**validated_data)

    def build(self):
        if not hasattr(self, "_errors"):
            self.is_valid(raise_exception=True)

        return self.save()

    def update(self, instance, validated_data):
        raise NotImplemented("`update()` not implemented.")
