# Generated by Django 2.0.2 on 2018-07-18 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0019_auto_20180718_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(to='mibandapp.Image'),
        ),
    ]
