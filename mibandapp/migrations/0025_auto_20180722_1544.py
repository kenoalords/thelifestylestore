# Generated by Django 2.0.2 on 2018-07-22 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0024_auto_20180720_0900'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productfeature',
            options={'ordering': ['feature__name']},
        ),
        migrations.RemoveField(
            model_name='product',
            name='features',
        ),
        migrations.AddField(
            model_name='productfeature',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mibandapp.Product'),
            preserve_default=False,
        ),
    ]