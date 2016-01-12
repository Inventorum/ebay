# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ebayaccountmodel',
            old_name='last_core_api_sync',
            new_name='last_core_products_sync',
        ),
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='last_core_orders_sync',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
