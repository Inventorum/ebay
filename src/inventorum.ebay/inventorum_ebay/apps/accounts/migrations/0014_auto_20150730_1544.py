# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_ebayaccountmodel_last_core_returns_sync'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayaccountmodel',
            name='inv_id',
            field=models.BigIntegerField(unique=True, verbose_name='Universal inventorum id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayusermodel',
            name='inv_id',
            field=models.BigIntegerField(unique=True, verbose_name='Universal inventorum id'),
            preserve_default=True,
        ),
    ]
