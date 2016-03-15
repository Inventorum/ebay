# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0005_auto_20150519_1026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingserviceconfigurationmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='shippingservicemodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='shippingserviceconfigurationmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shippingservicemodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
