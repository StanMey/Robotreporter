# Generated by Django 3.0.3 on 2020-09-30 21:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0005_auto_20200930_1704'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stocks',
            name='abs_delta',
        ),
        migrations.RemoveField(
            model_name='stocks',
            name='abs_perc',
        ),
    ]
