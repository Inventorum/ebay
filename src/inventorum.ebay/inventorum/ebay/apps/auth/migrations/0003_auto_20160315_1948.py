# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_auth', '0002_ebaytokenmodel_site_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebaytokenmodel',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='ebaytokenmodel',
            name='time_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last change'),
            preserve_default=True,
        ),
    ]
