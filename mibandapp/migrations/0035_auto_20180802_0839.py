# Generated by Django 2.0.2 on 2018-08-02 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0034_auto_20180727_1754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(null=True, to='mibandapp.Category'),
        ),
    ]
