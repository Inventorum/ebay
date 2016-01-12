# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_ebayproductmodel_external_item_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebayproductmodel',
            name='external_item_id',
        ),
        migrations.AddField(
            model_name='ebayitemmodel',
            name='ends_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayitemmodel',
            name='published_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayitemmodel',
            name='unpublished_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='publishing_status',
            field=models.IntegerField(default=1, choices=[(1, b'Draft'), (2, b'In progress'), (3, b'Published'), (4, b'Unpublished')]),
            preserve_default=True,
        ),
    ]
