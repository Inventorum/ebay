# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import datetime
import inventorum.util.django.db.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_auto_20150415_1623'),
        ('products', '0004_auto_20150413_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayProductSpecific',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('value', models.CharField(max_length=255)),
                ('specific', models.ForeignKey(related_name='+', to='categories.CategorySpecificModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
