# Generated by Django 3.1.6 on 2021-03-31 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Iconicity', '0004_auto_20210331_0712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='actor',
            field=models.JSONField(default=dict, max_length=500),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='object',
            field=models.JSONField(default=dict, max_length=500),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='type',
            field=models.CharField(default='follow', max_length=10),
        ),
        migrations.AlterField(
            model_name='like',
            name='type',
            field=models.CharField(default='like', max_length=10),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='follow',
            field=models.JSONField(default=dict, max_length=500),
        ),
    ]