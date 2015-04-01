# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__first__'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayaccountmodel',
            name='ebay_token',
            field=models.ForeignKey(related_name='accounts', verbose_name='Ebay token', blank=True, to='auth.EbayTokenModel', null=True),
            preserve_default=True,
        ),
    ]
