# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('name', models.CharField(max_length=255)),
                ('external_id', models.CharField(max_length=255)),
                ('external_parent_id', models.CharField(max_length=255)),
                ('b2b_vat_enabled', models.BooleanField(default=False)),
                ('best_offer_enabled', models.BooleanField(default=False)),
                ('auto_pay_enabled', models.BooleanField(default=False)),
                ('item_lot_size_disabled', models.BooleanField(default=False)),
                ('ebay_leaf', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent Category', blank=True, to='categories.CategoryModel', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
