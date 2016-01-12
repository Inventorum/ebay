# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='payment_method_bank_transfer_enabled',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='payment_method_paypal_email_address',
            field=models.EmailField(max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='payment_method_paypal_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
