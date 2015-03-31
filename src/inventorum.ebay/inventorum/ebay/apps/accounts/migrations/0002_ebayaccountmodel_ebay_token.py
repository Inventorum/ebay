# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='ebay_token',
            field=models.ForeignKey(related_name='accounts', verbose_name='Ebay token', blank=True, to='auth.EbayToken', null=True),
            preserve_default=True,
        ),
    ]
