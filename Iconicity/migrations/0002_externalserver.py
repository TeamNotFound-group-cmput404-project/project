# Generated by Django 3.1.6 on 2021-03-05 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Iconicity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalServer',
            fields=[
                ('host', models.URLField(default='', primary_key=True, serialize=False)),
            ],
        ),
    ]