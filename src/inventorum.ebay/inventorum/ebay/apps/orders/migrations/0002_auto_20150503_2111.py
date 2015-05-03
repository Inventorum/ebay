# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inventorum.ebay.lib.db.fields
import django_countries.fields
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordermodel',
            old_name='shipping',
            new_name='selected_shipping',
        ),
        migrations.RemoveField(
            model_name='orderlineitemmodel',
            name='inv_id',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='created_from_id',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='created_from_type',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='final_price',
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='buyer_email',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='buyer_first_name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='buyer_last_name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='original_ebay_data',
            field=django_extensions.db.fields.json.JSONField(null=True, verbose_name='Original ebay data'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='payment_amount',
            field=inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='payment_method',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='payment_status',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_address1',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_address2',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_city',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_first_name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_last_name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_postal_code',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='shipping_state',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='subtotal',
            field=inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='total',
            field=inventorum.ebay.lib.db.fields.MoneyField(null=True, max_digits=10, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='ebay_id',
            field=models.CharField(unique=True, max_length=255, verbose_name='Ebay id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='ebay_status',
            field=models.CharField(max_length=255, verbose_name='Ebay order status', choices=[('Complete', 'Complete'), ('Incomplete', 'Incomplete'), ('Pending', 'Pending')]),
            preserve_default=True,
        ),
    ]
