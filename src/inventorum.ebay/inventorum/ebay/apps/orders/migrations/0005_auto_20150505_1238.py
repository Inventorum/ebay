# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20150505_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatusModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('is_paid', models.BooleanField(default=False)),
                ('is_shipped', models.BooleanField(default=False)),
                ('is_closed', models.BooleanField(default=False)),
                ('is_canceled', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='core_status',
            field=models.OneToOneField(related_name='core_status_related_order', null=True, to='orders.OrderStatusModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='ebay_status',
            field=models.OneToOneField(related_name='ebay_status_related_order', null=True, to='orders.OrderStatusModel'),
            preserve_default=True,
        ),
    ]
