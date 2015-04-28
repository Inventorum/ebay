# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from django.db import models


log = logging.getLogger(__name__)


class MoneyField(models.DecimalField):

    def __init__(self, max_digits=10, decimal_places=2, **kwargs):
        super(MoneyField, self).__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)
