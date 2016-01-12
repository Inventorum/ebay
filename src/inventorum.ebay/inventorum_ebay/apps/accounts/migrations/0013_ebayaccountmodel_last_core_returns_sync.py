# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='last_core_returns_sync',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
