# Generated by Django 3.0.3 on 2020-10-06 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0008_site'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='site',
            options={'permissions': [('is_view_only', 'user_is_view_only')]},
        ),
    ]