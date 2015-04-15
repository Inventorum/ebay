# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.core.exceptions import ValidationError

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

        try:
            instance = ModelClass(**validated_data)
        except TypeError as e:
            msg = 'Got TypeError (%s) when trying to create %s with data: %s' % (e, ModelClass, validated_data)
            log.warn(msg)
            raise ValidationError(msg)

        # Debugging purposes
        instance._poposerializer_original_data = self.root.initial_data
        return instance

    def build(self):
        if not hasattr(self, "_errors"):
            self.is_valid(raise_exception=True)

        return self.save()

    def update(self, instance, validated_data):
        raise NotImplemented("`update()` not implemented.")