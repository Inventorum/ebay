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
        ('accounts', '0006_ebayaccountmodel_last_core_api_sync'),
        ('shipping', '0004_auto_20150429_0036'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderLineItemModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('inv_id', models.IntegerField(unique=True, null=True, verbose_name='Universal inventorum id', blank=True)),
                ('ebay_id', models.CharField(max_length=255, verbose_name='Ebay transaction id')),
                ('orderable_item_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
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
                ('final_price', inventorum.ebay.lib.db.fields.MoneyField(verbose_name='Final price on ebay', max_digits=10, decimal_places=2)),
                ('ebay_status', models.CharField(max_length=255, choices=[('Complete', 'Complete'), ('Incomplete', 'Incomplete'), ('Pending', 'Pending')])),
                ('created_from_id', models.PositiveIntegerField(null=True, blank=True)),
                ('account', models.ForeignKey(verbose_name='Ebay account', to='accounts.EbayAccountModel')),
                ('created_from_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('shipping', models.OneToOneField(related_name='order', null=True, blank=True, to='shipping.ShippingServiceConfigurationModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='orderlineitemmodel',
            name='order',
            field=models.ForeignKey(related_name='line_items', verbose_name='Order', to='orders.OrderModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderlineitemmodel',
            name='orderable_item_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
    ]
