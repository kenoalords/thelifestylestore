# Generated by Django 2.0.2 on 2018-07-17 21:19

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0012_order_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(max_length=6)),
                ('channel', models.CharField(max_length=6)),
                ('ip_address', models.GenericIPAddressField()),
                ('reference', models.CharField(max_length=64)),
                ('customer_first_name', models.CharField(max_length=64)),
                ('customer_last_name', models.CharField(max_length=64)),
                ('customer_code', models.CharField(max_length=64)),
                ('customer_email', models.EmailField(max_length=128)),
                ('customer_id', models.IntegerField()),
                ('paid_date', models.DateTimeField(default=datetime.datetime(2018, 7, 17, 21, 19, 0, 235651, tzinfo=utc))),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mibandapp.Order')),
            ],
        ),
    ]
