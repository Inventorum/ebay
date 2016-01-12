# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0002_shippingserviceconfigurationmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingserviceconfigurationmodel',
            name='additional_cost',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
