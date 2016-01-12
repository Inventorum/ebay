# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0007_categoryfeaturesmodel_variations_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorymodel',
            name='name',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
