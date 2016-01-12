# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_ebayaccountmodel_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='last_core_api_sync',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
