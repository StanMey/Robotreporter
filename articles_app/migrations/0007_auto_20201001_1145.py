# Generated by Django 3.0.3 on 2020-10-01 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0006_auto_20200930_2140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stocks',
            old_name='index',
            new_name='indexx',
        ),
    ]
