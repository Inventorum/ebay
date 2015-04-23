# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20150422_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemimagemodel',
            name='variation',
            field=models.ForeignKey(related_name='images', blank=True, to='products.EbayItemVariationModel', null=True),
            preserve_default=True,
        ),
    ]
