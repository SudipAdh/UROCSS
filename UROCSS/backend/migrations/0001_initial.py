# Generated by Django 3.0.6 on 2020-05-24 15:54

from django.db import migrations, models
import phone_field.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('age', models.IntegerField(max_length=3)),
                ('shop_name', models.CharField(max_length=200)),
                ('shop_address', models.CharField(max_length=200)),
                ('contact_number', phone_field.models.PhoneField(blank=True, max_length=10)),
            ],
        ),
    ]