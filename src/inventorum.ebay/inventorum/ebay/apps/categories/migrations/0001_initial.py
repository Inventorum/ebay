# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_countries.fields
from django.utils.timezone import utc
import django.utils.timezone
import mptt.fields
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('name', models.CharField(max_length=255)),
                ('external_id', models.CharField(max_length=255)),
                ('external_parent_id', models.CharField(max_length=255, null=True, blank=True)),
                ('b2b_vat_enabled', models.BooleanField(default=False)),
                ('best_offer_enabled', models.BooleanField(default=False)),
                ('auto_pay_enabled', models.BooleanField(default=False)),
                ('item_lot_size_disabled', models.BooleanField(default=False)),
                ('ebay_leaf', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, to='categories.CategoryModel', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
