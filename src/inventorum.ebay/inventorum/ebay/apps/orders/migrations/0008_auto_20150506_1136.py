# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import inventorum.ebay.lib.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_orderlineitemmodel_tax_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitemmodel',
            name='tax_rate',
            field=inventorum.ebay.lib.db.fields.TaxRateField(verbose_name='Tax rate', max_digits=10, decimal_places=3),
            preserve_default=True,
        ),
    ]
