# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inventorum_ebay.lib.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20150505_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderlineitemmodel',
            name='tax_rate',
            field=inventorum_ebay.lib.db.fields.TaxRateField(null=True, verbose_name='Tax rate', max_digits=10, decimal_places=3, blank=True),
            preserve_default=True,
        ),
    ]
