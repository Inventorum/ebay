# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from django.db import models
from django_extensions.db.fields.json import JSONField as DjangoExtensionsJSONField, dumps

log = logging.getLogger(__name__)


class MoneyField(models.DecimalField):

    def __init__(self, max_digits=10, decimal_places=2, **kwargs):
        super(MoneyField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)


class TaxRateField(models.DecimalField):

    def __init__(self, max_digits=10, decimal_places=3, **kwargs):
        super(TaxRateField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)


class JSONField(DjangoExtensionsJSONField):
    def get_db_prep_save(self, *args, **kwargs):
        """
        We need to override this method because the implementation coming from Django Extensions will try to save
        non-JSON structure which in turn will render the data useless for deserialisation.
        """
        value = super(JSONField, self).get_db_prep_save(*args, **kwargs)
        return dumps(value)
