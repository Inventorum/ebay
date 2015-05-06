# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext

from rest_framework import serializers


log = logging.getLogger(__name__)


# Note: There are no specific test cases yet but the field is implicitly tested in `TestEbayProductSerializer`
class RelatedModelByIdField(serializers.PrimaryKeyRelatedField):
    """
    A field for related models, which works similar to `PrimaryKeyRelatedField` but allows
    a verbose representation with a given `serializer` as opposed to just serialize the pk.

    Likewise, it expects a JSON object for deserialization with an `id` attribute.
    """

    def __init__(self, **kwargs):
        assert 'serializer' in kwargs
        self.serializer = kwargs['serializer']
        del kwargs['serializer']

        if 'queryset' not in kwargs:
            assert 'Meta' in self.serializer.__dict__
            assert 'model' in self.serializer.Meta.__dict__
            kwargs['queryset'] = self.serializer.Meta.model.objects.all()

        super(RelatedModelByIdField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        id = data.get("id", None)
        if id is None:
            raise ValidationError(ugettext("id is required"))

        return super(RelatedModelByIdField, self).to_internal_value(id)

    def to_representation(self, value):
        return self.serializer(value).data


class MoneyField(serializers.DecimalField):

    def __init__(self, max_digits=10, decimal_places=2, **kwargs):
        super(MoneyField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)


class TaxRateField(serializers.DecimalField):

    def __init__(self, max_digits=10, decimal_places=3, **kwargs):
        super(TaxRateField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)
