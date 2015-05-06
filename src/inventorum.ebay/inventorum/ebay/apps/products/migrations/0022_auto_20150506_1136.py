# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inventorum.ebay.lib.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_auto_20150505_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemmodel',
            name='tax_rate',
            field=inventorum.ebay.lib.db.fields.TaxRateField(null=True, max_digits=10, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayitemvariationmodel',
            name='tax_rate',
            field=inventorum.ebay.lib.db.fields.TaxRateField(null=True, max_digits=10, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='gross_price',
            field=inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemvariationmodel',
            name='gross_price',
            field=inventorum.ebay.lib.db.fields.MoneyField(max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
