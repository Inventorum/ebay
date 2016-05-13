# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_countries.fields
from django.utils.timezone import utc
import django.utils.timezone
import inventorum.util.django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_auth', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_added', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('time_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last change', auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('deleted_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='Time of deletion')),
                ('name', models.CharField(max_length=255)),
                ('street', models.CharField(max_length=255, null=True, blank=True)),
                ('street1', models.CharField(max_length=255, null=True, blank=True)),
                ('city', models.CharField(max_length=255, null=True, blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('postal_code', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(inventorum.util.django.db.models.ModelMixins, models.Model),
        ),
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='registration_address',
            field=models.ForeignKey(related_name='accounts', verbose_name='Registration address', blank=True, to='accounts.AddressModel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='token',
            field=models.ForeignKey(related_name='accounts', verbose_name='Ebay token', blank=True,
                                    to='ebay_auth.EbayTokenModel', null=True),
            preserve_default=True,
        ),
    ]
