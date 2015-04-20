# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_auto_20150414_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategorySpecificModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('name', models.CharField(max_length=255)),
                ('help_text', models.TextField(null=True, blank=True)),
                ('help_url', models.URLField(null=True, blank=True)),
                ('can_use_in_variations', models.BooleanField(default=True)),
                ('max_values', models.IntegerField()),
                ('min_values', models.IntegerField()),
                ('selection_mode', models.CharField(max_length=255)),
                ('value_type', models.CharField(max_length=255)),
                ('category', models.ForeignKey(related_name='specifics', to='categories.CategoryModel')),
            ],
            options={
                'ordering': ('name', 'time_added', 'pk'),
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='SpecificValueModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('value', models.CharField(max_length=255)),
                ('specific', models.ForeignKey(related_name='values', to='categories.CategorySpecificModel')),
            ],
            options={
                'ordering': ('time_added', 'pk'),
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='categoryspecificmodel',
            unique_together=set([('category', 'name', 'deleted_at')]),
        ),
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='item_specifics_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
