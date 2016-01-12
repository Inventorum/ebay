# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_auto_20150424_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemvariationmodel',
            name='inv_id',
            field=models.IntegerField(default=1, unique=True, verbose_name='Universal inventorum id'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='gross_price',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='quantity',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
