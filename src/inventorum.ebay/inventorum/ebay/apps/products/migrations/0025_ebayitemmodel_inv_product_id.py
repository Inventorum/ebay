# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_auto_20150506_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemmodel',
            name='inv_product_id',
            field=models.IntegerField(null=True, verbose_name='Inventorum product id', blank=True),
            preserve_default=True,
        ),
    ]
