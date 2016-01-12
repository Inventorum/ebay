# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_ebayaccountmodel_ebay_location_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='last_ebay_orders_sync',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
