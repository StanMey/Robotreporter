# Generated by Django 3.0.3 on 2020-10-14 17:48

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0015_auto_20201014_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='observations',
            name='meta_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
