# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0009_auto_20150730_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoryfeaturesmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='categoryspecificmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='durationmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='paymentmethodmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='specificvaluemodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='categoryfeaturesmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='categoryspecificmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='durationmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='paymentmethodmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='specificvaluemodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
