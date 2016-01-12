# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_ebayaccountmodel_last_ebay_orders_sync'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_address1',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_address2',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_city',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_country',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_first_name',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_last_name',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_postal_code',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='shipping_state',
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='billing_address',
            field=models.OneToOneField(related_name='billing_order', null=True, blank=True, to='accounts.AddressModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_address',
            field=models.OneToOneField(related_name='shipping_order', null=True, blank=True, to='accounts.AddressModel'),
            preserve_default=True,
        ),
    ]
