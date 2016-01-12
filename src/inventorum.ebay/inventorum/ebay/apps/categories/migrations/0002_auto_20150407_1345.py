# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryFeaturesModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('category', models.OneToOneField(related_name='features', to='categories.CategoryModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='DurationModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('value', models.CharField(max_length=255, unique_for_date='deleted_at')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='PaymentMethodModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('value', models.CharField(max_length=255, unique_for_date='deleted_at')),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='durations',
            field=models.ManyToManyField(related_name='features', to='categories.DurationModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='categoryfeaturesmodel',
            name='payment_methods',
            field=models.ManyToManyField(related_name='features', to='categories.PaymentMethodModel'),
            preserve_default=True,
        ),
    ]
