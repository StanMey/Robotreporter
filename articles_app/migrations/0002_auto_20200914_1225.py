# Generated by Django 3.0.3 on 2020-09-14 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stocks',
            name='company_name',
        ),
        migrations.AddField(
            model_name='stocks',
            name='stock',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
