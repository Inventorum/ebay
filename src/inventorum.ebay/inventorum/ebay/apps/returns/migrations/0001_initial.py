# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import inventorum.ebay.lib.db.fields
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20150601_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnItemModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('inv_id', models.IntegerField(unique=True, verbose_name='Universal inventorum id')),
                ('refund_amount', inventorum.ebay.lib.db.fields.MoneyField(max_digits=10, decimal_places=2)),
                ('refund_quantity', models.IntegerField()),
                ('order_line_item', models.ForeignKey(related_name='items', to='orders.OrderLineItemModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='ReturnModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('inv_id', models.IntegerField(unique=True, verbose_name='Universal inventorum id')),
                ('synced_with_ebay', models.BooleanField(default=False)),
                ('refund_type', models.CharField(max_length=255, choices=[('EBAY', 'Refund by Ebay')])),
                ('refund_amount', inventorum.ebay.lib.db.fields.MoneyField(max_digits=10, decimal_places=2)),
                ('refund_note', models.TextField(default='')),
                ('order', models.ForeignKey(related_name='returns', to='orders.OrderModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
