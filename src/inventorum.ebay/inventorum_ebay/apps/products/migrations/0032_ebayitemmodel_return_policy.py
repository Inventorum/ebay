# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0004_returnpolicymodel'),
        ('products', '0031_auto_20150902_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemmodel',
            name='return_policy',
            field=models.OneToOneField(related_name='item', null=True, blank=True, to='returns.ReturnPolicyModel'),
            preserve_default=True,
        ),
    ]
