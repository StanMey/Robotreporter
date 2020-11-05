# Generated by Django 3.0.3 on 2020-11-05 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0021_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='score',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
