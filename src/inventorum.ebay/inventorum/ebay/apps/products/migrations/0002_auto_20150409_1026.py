# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_countries.fields
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20150401_1105'),
        ('categories', '0003_auto_20150407_1423'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayItemImageModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('inv_id', models.IntegerField(unique=True, verbose_name='Universal inventorum id')),
                ('url', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='EbayItemModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('name', models.CharField(max_length=255)),
                ('listing_duration', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('postal_code', models.CharField(max_length=255, null=True, blank=True)),
                ('quantity', models.IntegerField(default=0)),
                ('gross_price', models.DecimalField(max_digits=20, decimal_places=10)),
                ('publishing_status', models.IntegerField(default=1, choices=[(1, b'Draft'), (2, b'In progress'), (3, b'Published')])),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('account', models.ForeignKey(related_name='items', verbose_name='Inventorum ebay account', to='accounts.EbayAccountModel')),
                ('category', models.ForeignKey(related_name='items', to='categories.CategoryModel')),
                ('product', models.ForeignKey(related_name='items', to='products.EbayProductModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='EbayItemShippingDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('additional_cost', models.DecimalField(max_digits=20, decimal_places=10)),
                ('cost', models.DecimalField(max_digits=20, decimal_places=10)),
                ('external_id', models.CharField(max_length=255)),
                ('item', models.ForeignKey(related_name='shipping', to='products.EbayItemModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ebayitemimagemodel',
            name='item',
            field=models.ForeignKey(related_name='images', to='products.EbayItemModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='category',
            field=models.ForeignKey(related_name='products', blank=True, to='categories.CategoryModel', null=True),
            preserve_default=True,
        ),
    ]
