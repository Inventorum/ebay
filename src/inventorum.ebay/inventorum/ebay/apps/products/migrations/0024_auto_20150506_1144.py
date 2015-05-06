# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inventorum.ebay.lib.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_auto_20150506_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayitemvariationmodel',
            name='tax_rate',
            field=inventorum.ebay.lib.db.fields.TaxRateField(max_digits=10, decimal_places=3),
            preserve_default=True,
        ),
    ]
