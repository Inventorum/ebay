# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_ebayitemmodel_is_click_and_collect'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemvariationmodel',
            name='inv_product_id',
            field=models.IntegerField(default=1, verbose_name='Inventorum product id'),
            preserve_default=False,
        ),
    ]
