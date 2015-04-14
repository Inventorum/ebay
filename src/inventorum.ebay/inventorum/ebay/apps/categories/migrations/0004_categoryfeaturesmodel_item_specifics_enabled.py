# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_auto_20150407_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='item_specifics_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
