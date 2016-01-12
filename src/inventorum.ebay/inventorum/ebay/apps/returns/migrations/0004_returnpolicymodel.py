# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import datetime
import inventorum.util.django.db.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0003_auto_20150730_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnPolicyModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('returns_accepted_option', models.CharField(max_length=255, null=True, blank=True)),
                ('returns_within_option', models.CharField(max_length=255, null=True, blank=True)),
                ('shipping_cost_paid_by_option', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
