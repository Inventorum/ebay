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
        ('shipping', '0003_auto_20150425_1216'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('orderable_item_id', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity')),
                ('unit_price', inventorum.ebay.lib.db.fields.MoneyField(verbose_name='Unit price', max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('inv_id', models.IntegerField(unique=True, null=True, verbose_name='Universal inventorum id', blank=True)),
                ('ebay_id', models.CharField(max_length=255, verbose_name='Ebay id')),
                ('total_price', inventorum.ebay.lib.db.fields.MoneyField(verbose_name='Total price incl. shipping', max_digits=10, decimal_places=2)),
                ('shipping_service', models.OneToOneField(null=True, blank=True, to='shipping.ShippingServiceConfigurationModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='orderlineitem',
            name='order',
            field=models.ForeignKey(related_name='line_items', verbose_name='Order', to='orders.OrderModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderlineitem',
            name='orderable_item_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
    ]
