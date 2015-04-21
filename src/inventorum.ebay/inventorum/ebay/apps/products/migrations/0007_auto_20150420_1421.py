# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django_extensions.db.fields.json
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_ebayitemspecificmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='EbayApiAttempt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('type', models.CharField(max_length=255, choices=[(b'publish', b'Publish'), (b'unpublish', b'Unpublish')])),
                ('success', models.BooleanField()),
                ('item', models.ForeignKey(related_name='attempts', blank=True, to='products.EbayItemModel', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='EbayApiAttemptRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('body', models.TextField()),
                ('headers', django_extensions.db.fields.json.JSONField()),
                ('url', models.TextField()),
                ('method', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.CreateModel(
            name='EbayApiAttemptResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('content', models.TextField()),
                ('headers', django_extensions.db.fields.json.JSONField()),
                ('url', models.TextField()),
                ('status_code', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ebayapiattempt',
            name='request',
            field=models.OneToOneField(related_name='attempt', to='products.EbayApiAttemptRequest'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayapiattempt',
            name='response',
            field=models.OneToOneField(related_name='attempt', to='products.EbayApiAttemptResponse'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ebayitemmodel',
            name='publishing_status',
            field=models.IntegerField(default=1, choices=[(1, b'Draft'), (2, b'In progress'), (3, b'Published'), (5, b'Failed')]),
            preserve_default=True,
        ),
    ]
