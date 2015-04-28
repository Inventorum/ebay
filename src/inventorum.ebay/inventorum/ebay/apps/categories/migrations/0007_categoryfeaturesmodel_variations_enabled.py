# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0006_auto_20150420_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='variations_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
