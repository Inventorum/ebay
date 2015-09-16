# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_ebayproductmodel_ean_does_not_apply'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemmodel',
            name='ebay_seller_profile_return_policy_id',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
