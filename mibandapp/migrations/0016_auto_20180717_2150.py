# Generated by Django 2.0.2 on 2018-07-17 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0015_auto_20180717_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='customer_first_name',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='customer_last_name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]