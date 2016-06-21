# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20150504_1452'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordermodel',
            old_name='ebay_status',
            new_name='ebay_complete_status',
        ),
    ]
