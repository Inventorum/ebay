# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0002_auto_20150609_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returnitemmodel',
            name='inv_id',
            field=models.BigIntegerField(unique=True, verbose_name='Universal inventorum id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='returnmodel',
            name='inv_id',
            field=models.BigIntegerField(unique=True, verbose_name='Universal inventorum id'),
            preserve_default=True,
        ),
    ]
