# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_auto_20150422_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayItemUpdateModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('quantity', models.IntegerField(null=True, blank=True)),
                ('gross_price', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('status', models.IntegerField(default=1, choices=[(1, 'DRAFT'), (2, 'IN_PROGRESS'), (3, 'SUCCEEDED'), (4, 'FAILED')])),
                ('item', models.ForeignKey(related_name='updates', to='products.EbayItemModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ebayproductmodel',
            name='deleted_in_core_api',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='publishing_status',
            field=models.CharField(default='draft', max_length=255, choices=[('draft', 'Draft'), ('in_progress', 'In progress'), ('published', 'Published'), ('unpublished', 'Unpublished'), ('failed', 'Failed')]),
            preserve_default=True,
        ),
    ]
