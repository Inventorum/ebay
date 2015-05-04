# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_ebayaccountmodel_last_ebay_orders_sync'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressmodel',
            name='state',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
