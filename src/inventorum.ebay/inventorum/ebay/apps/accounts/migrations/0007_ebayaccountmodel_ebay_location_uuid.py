# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_ebayaccountmodel_last_core_api_sync'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='ebay_location_uuid',
            field=models.CharField(max_length=36, null=True, blank=True),
            preserve_default=True,
        ),
    ]
