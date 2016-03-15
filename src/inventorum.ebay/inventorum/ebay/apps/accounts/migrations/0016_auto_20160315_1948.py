# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_ebayaccountmodel_return_policy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayaccountmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebaylocationmodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ebayusermodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='addressmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayaccountmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebaylocationmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayusermodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
