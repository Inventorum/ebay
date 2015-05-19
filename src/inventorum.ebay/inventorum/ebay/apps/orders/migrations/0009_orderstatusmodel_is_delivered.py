# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20150506_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderstatusmodel',
            name='is_delivered',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
