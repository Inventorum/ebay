# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_ebayitemvariationupdatemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayproductmodel',
            name='is_click_and_collect',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
