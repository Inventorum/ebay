# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_auto_20150424_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayItemVariationUpdateModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('quantity', models.IntegerField(null=True, blank=True)),
                ('gross_price', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('status', models.CharField(default='draft', max_length=255, choices=[('draft', 'DRAFT'), ('in_progress', 'IN_PROGRESS'), ('succeeded', 'SUCCEEDED'), ('failed', 'FAILED')])),
                ('status_details', django_extensions.db.fields.json.JSONField()),
                ('update_item', models.ForeignKey(related_name='variations', to='products.EbayItemUpdateModel')),
                ('variation', models.ForeignKey(related_name='updates', to='products.EbayItemVariationModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
