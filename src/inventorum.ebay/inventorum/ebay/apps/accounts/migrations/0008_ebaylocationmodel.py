# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import datetime
import inventorum.util.django.db.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_ebayaccountmodel_ebay_location_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayLocationModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('latitude', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('pickup_instruction', models.TextField(null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('account', models.OneToOneField(related_name='location', to='accounts.EbayAccountModel')),
                ('address', models.ForeignKey(related_name='locations', verbose_name='Registration address', blank=True, to='accounts.AddressModel', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
