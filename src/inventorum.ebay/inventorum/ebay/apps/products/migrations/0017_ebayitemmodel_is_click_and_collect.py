# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_ebayproductmodel_is_click_and_collect'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemmodel',
            name='is_click_and_collect',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
