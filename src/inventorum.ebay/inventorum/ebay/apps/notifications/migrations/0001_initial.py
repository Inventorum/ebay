# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models
from inventorum.ebay.lib.db.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EbayNotificationModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('event_type', models.CharField(max_length=255)),
                ('payload', JSONField()),
                ('timestamp', models.CharField(max_length=255)),
                ('signature', models.CharField(max_length=255)),
                ('request_body', models.TextField()),
                ('status', models.CharField(default='unhandled', max_length=255, choices=[('unhandled', 'unhandled'), ('handled', 'handled'), ('failed', 'failed')])),
                ('status_details', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
    ]
