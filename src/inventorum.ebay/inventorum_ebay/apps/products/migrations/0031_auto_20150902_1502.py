# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_ebayproductmodel_ean_does_not_apply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayitemimagemodel',
            name='inv_image_id',
            field=models.IntegerField(null=True, verbose_name='Inventorum image id', blank=True),
            preserve_default=True,
        ),
    ]
