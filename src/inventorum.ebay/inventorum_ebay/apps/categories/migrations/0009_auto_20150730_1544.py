# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0008_auto_20150519_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='ean_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='ean_required',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
