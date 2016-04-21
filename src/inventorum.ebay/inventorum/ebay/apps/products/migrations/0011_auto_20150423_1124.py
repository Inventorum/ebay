# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from inventorum.ebay.lib.db.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20150422_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayapiattempt',
            name='item_update',
            field=models.ForeignKey(related_name='attempts', blank=True, to='products.EbayItemUpdateModel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayitemupdatemodel',
            name='status_details',
            field=JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayapiattempt',
            name='type',
            field=models.CharField(max_length=255, choices=[('publish', 'Publish'), ('unpublish', 'Unpublish'), ('update', 'Update')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemupdatemodel',
            name='status',
            field=models.CharField(default='draft', max_length=255, choices=[('draft', 'DRAFT'), ('in_progress', 'IN_PROGRESS'), ('succeeded', 'SUCCEEDED'), ('failed', 'FAILED')]),
            preserve_default=True,
        ),
    ]
