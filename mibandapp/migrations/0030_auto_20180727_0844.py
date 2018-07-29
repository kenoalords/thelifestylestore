# Generated by Django 2.0.2 on 2018-07-27 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mibandapp', '0029_productlike_productnotification'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSlider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=512)),
                ('image', models.ImageField(upload_to='uploads/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShippingZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12)),
                ('kg_cost', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.5, max_digits=4),
        ),
        migrations.AddField(
            model_name='productslider',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mibandapp.Product'),
        ),
    ]