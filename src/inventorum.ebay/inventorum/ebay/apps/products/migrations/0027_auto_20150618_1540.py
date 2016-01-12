# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_auto_20150618_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='inv_product_id',
            field=models.IntegerField(verbose_name='Inventorum product id'),
            preserve_default=True,
        ),
    ]
