# Generated by Django 3.0.3 on 2020-11-05 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0018_articles_image_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='image_file',
            field=models.ImageField(null=True, upload_to='images/', verbose_name=''),
        ),
    ]
