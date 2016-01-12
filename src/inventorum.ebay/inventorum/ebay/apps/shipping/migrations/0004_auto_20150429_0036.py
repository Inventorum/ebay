# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('shipping', '0003_auto_20150425_1216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingserviceconfigurationmodel',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='shippingserviceconfigurationmodel',
            name='object_id',
        ),
        migrations.AddField(
            model_name='shippingserviceconfigurationmodel',
            name='entity_id',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shippingserviceconfigurationmodel',
            name='entity_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
