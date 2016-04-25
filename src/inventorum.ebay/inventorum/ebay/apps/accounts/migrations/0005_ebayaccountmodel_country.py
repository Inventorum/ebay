# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20150401_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
            preserve_default=True,
        ),
    ]
