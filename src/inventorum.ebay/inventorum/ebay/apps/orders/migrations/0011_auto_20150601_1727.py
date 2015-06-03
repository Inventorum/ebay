# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_ordermodel_pickup_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderlineitemmodel',
            name='inv_id',
            field=models.IntegerField(unique=True, null=True, verbose_name='Universal inventorum id', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='pickup_code',
            field=models.CharField(max_length=6, null=True, blank=True),
            preserve_default=True,
        ),
    ]
