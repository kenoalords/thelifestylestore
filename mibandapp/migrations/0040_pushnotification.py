# Generated by Django 2.0.2 on 2018-08-22 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0039_shippingzone_additional_kg_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(max_length=564)),
                ('auth', models.CharField(max_length=256, null=True)),
                ('p256dh', models.CharField(max_length=256, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
