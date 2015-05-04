# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20150504_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordermodel',
            old_name='payment_status',
            new_name='ebay_payment_method',
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='ebay_payment_status',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='payment_method',
            field=models.CharField(blank=True, max_length=255, null=True, choices=[('4', 'PayPal'), ('6', 'Bank Transfer')]),
            preserve_default=True,
        ),
    ]
