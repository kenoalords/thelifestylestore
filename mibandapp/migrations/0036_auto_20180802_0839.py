# Generated by Django 2.0.2 on 2018-08-02 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0035_auto_20180802_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(to='mibandapp.Category'),
        ),
    ]
