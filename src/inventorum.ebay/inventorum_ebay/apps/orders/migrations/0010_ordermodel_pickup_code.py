# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_orderstatusmodel_is_delivered'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermodel',
            name='pickup_code',
            field=models.CharField(max_length=12, null=True, blank=True),
            preserve_default=True,
        ),
    ]
