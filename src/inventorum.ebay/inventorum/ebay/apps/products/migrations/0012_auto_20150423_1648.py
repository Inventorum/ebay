# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models
from inventorum.ebay.lib.db.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20150423_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayItemVariationModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('quantity', models.IntegerField(default=0)),
                ('gross_price', models.DecimalField(max_digits=20, decimal_places=10)),
                ('item', models.ForeignKey(related_name='variations', to='products.EbayItemModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='EbayItemVariationSpecificModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('name', models.CharField(max_length=255)),
                ('variation', models.ForeignKey(related_name='specifics', to='products.EbayItemVariationModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='EbayItemVariationSpecificValueModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('value', models.CharField(max_length=255)),
                ('specific', models.ForeignKey(related_name='values', to='products.EbayItemVariationSpecificModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ebayitemimagemodel',
            name='variation',
            field=models.ForeignKey(related_name='images', blank=True, to='products.EbayItemVariationModel', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemimagemodel',
            name='item',
            field=models.ForeignKey(related_name='images', blank=True, to='products.EbayItemModel', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='publishing_status_details',
            field=JSONField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
