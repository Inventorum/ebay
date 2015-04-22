# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20150420_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitemmodel',
            name='publishing_status_details',
            field=jsonfield.fields.JSONField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='publishing_status',
            field=models.CharField(default=b'draft', max_length=255, choices=[(b'draft', b'Draft'), (b'in_progress', b'In progress'), (b'published', b'Published'), (b'failed', b'Failed')]),
            preserve_default=True,
        ),
    ]
