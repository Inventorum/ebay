# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20150421_1901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayapiattempt',
            name='success',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
