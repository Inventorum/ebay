# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_ebayitemvariationmodel_inv_product_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemimagemodel',
            name='inv_image_id',
            field=models.IntegerField(default=1, verbose_name='Inventorum image id'),
            preserve_default=False,
        ),
    ]
