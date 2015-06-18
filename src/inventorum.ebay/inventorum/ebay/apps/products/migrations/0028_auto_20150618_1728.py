# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_auto_20150618_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='inv_product_id',
            field=models.BigIntegerField(verbose_name='Inventorum product id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemvariationmodel',
            name='inv_product_id',
            field=models.BigIntegerField(verbose_name='Inventorum product id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayproductmodel',
            name='inv_id',
            field=models.BigIntegerField(unique=True, verbose_name='Universal inventorum id'),
            preserve_default=True,
        ),
    ]
