# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_auto_20150407_1423'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayImageModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('inv_id', models.IntegerField(unique=True, verbose_name='Universal inventorum id')),
                ('url', models.TextField()),
                ('product', models.ForeignKey(related_name='images', to='products.EbayProductModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='category',
            field=models.ForeignKey(related_name='products', default=0, to='categories.CategoryModel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='gross_price',
            field=models.DecimalField(default=0, max_digits=20, decimal_places=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='postal_code',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='publishing_status',
            field=models.IntegerField(default=1, choices=[(1, b'Draft'), (2, b'In progress'), (3, b'Published')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='quantity',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
