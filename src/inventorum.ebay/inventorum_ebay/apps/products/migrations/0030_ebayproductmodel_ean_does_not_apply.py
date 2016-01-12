# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_auto_20150730_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayproductmodel',
            name='ean_does_not_apply',
            field=models.BooleanField(default=False, verbose_name='Product has and cannot have EAN'),
            preserve_default=True,
        ),
    ]
