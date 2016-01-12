# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0004_returnpolicymodel'),
        ('accounts', '0014_auto_20150730_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='return_policy',
            field=models.OneToOneField(related_name='account', null=True, blank=True, to='returns.ReturnPolicyModel'),
            preserve_default=True,
        ),
    ]
