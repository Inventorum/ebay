# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20150601_1727'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderlineitemmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='orderstatusmodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='orderlineitemmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderstatusmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
