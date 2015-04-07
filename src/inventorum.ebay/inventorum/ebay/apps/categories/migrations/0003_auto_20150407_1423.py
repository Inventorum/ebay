# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_auto_20150407_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorymodel',
            name='external_id',
            field=models.CharField(max_length=255, unique_for_date='deleted_at'),
            preserve_default=True,
        ),
    ]
