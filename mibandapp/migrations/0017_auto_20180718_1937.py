# Generated by Django 2.0.2 on 2018-07-18 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0016_auto_20180717_2150'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='uploads/'),
        ),
    ]
