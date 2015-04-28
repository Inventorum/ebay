# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20150423_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayproductmodel',
            name='category',
            field=models.ForeignKey(related_name='products', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='categories.CategoryModel', null=True),
            preserve_default=True,
        ),
    ]
