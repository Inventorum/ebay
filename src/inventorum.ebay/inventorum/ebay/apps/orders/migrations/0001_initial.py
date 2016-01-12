# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import inventorum.ebay.lib.db.fields
import django_countries.fields
from django.utils.timezone import utc
import django_extensions.db.fields.json
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('shipping', '0004_auto_20150429_0036'),
        ('accounts', '0008_ebayaccountmodel_last_ebay_orders_sync'),
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
                ('ebay_id', models.CharField(unique=True, max_length=255, verbose_name='Ebay id')),
                ('ebay_status', models.CharField(max_length=255, verbose_name='Ebay order status', choices=[('Complete', 'Complete'), ('Incomplete', 'Incomplete'), ('Pending', 'Pending')])),
                ('original_ebay_data', django_extensions.db.fields.json.JSONField(null=True, verbose_name='Original ebay data')),
                ('buyer_first_name', models.CharField(max_length=255, null=True, blank=True)),
                ('buyer_last_name', models.CharField(max_length=255, null=True, blank=True)),
                ('buyer_email', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_first_name', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_last_name', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_address1', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_address2', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_postal_code', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_city', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_state', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('subtotal', inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('total', inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('payment_method', models.CharField(max_length=255, null=True, blank=True)),
                ('payment_amount', inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('payment_status', models.CharField(max_length=255, null=True, blank=True)),
                ('account', models.ForeignKey(verbose_name='Ebay account', to='accounts.EbayAccountModel')),
                ('selected_shipping', models.OneToOneField(related_name='order', null=True, blank=True, to='shipping.ShippingServiceConfigurationModel')),
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
