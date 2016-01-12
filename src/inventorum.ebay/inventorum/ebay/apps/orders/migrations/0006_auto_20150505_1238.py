# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20150505_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermodel',
            name='core_status',
            field=models.OneToOneField(related_name='core_status_related_order', to='orders.OrderStatusModel'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='ebay_status',
            field=models.OneToOneField(related_name='ebay_status_related_order', to='orders.OrderStatusModel'),
            preserve_default=True,
        ),
    ]
