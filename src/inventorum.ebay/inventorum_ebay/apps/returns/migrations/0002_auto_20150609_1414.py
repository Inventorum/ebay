# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnitemmodel',
            name='return_model',
            field=models.ForeignKey(related_name='items', default=None, to='returns.ReturnModel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='returnitemmodel',
            name='order_line_item',
            field=models.ForeignKey(related_name='return_items', to='orders.OrderLineItemModel'),
            preserve_default=True,
        ),
    ]
