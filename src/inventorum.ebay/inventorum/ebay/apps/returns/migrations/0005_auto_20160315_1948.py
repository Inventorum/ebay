# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0004_returnpolicymodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returnitemmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='returnmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='returnpolicymodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='returnitemmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='returnmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='returnpolicymodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
