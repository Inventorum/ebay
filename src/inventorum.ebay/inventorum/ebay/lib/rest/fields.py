# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import decimal
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet
from django.utils.encoding import smart_text
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

class InventorumNormalizedDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        data = smart_text(data).strip()
        if len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            value = decimal.Decimal(data)
        except decimal.DecimalException:
            self.fail('invalid')

        # Check for NaN. It is the only value that isn't equal to itself,
        # so we can use this to identify NaN values.
        if value != value:
            self.fail('invalid')

        # Check for infinity and negative infinity.
        if value in (decimal.Decimal('Inf'), decimal.Decimal('-Inf')):
            self.fail('invalid')

        # MH: This is what differs from original implementation of DecimalField!
        value = value.normalize()

        return super(InventorumNormalizedDecimalField, self).to_internal_value(value)


class MoneyField(InventorumNormalizedDecimalField):
    def __init__(self, max_digits=12, decimal_places=2, **kwargs):
        super(MoneyField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)


class TaxRateField(InventorumNormalizedDecimalField):
    def __init__(self, max_digits=13, decimal_places=3, **kwargs):
        super(TaxRateField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)


class InvIdField(serializers.Field):
    default_error_messages = {
        'invalid': _('A valid number is required.'),
    }

    def to_representation(self, inv_id_as_long):
        return str(inv_id_as_long)

    def to_internal_value(self, inv_id_as_str):
        try:
            return long(inv_id_as_str)
        except ValueError:
            self.fail('invalid')


class LazyPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    default_lookup_field = 'pk'

    def __init__(self, *args, **kwargs):
        self.lookup_field = kwargs.pop('lookup_field', self.default_lookup_field)
        super(LazyPrimaryKeyRelatedField, self).__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset(self)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated whenever used.
            queryset = queryset.all()
        return queryset


    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.lookup_field: data})
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        return getattr(value, self.lookup_field)
