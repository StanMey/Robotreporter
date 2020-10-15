# Generated by Django 3.0.3 on 2020-10-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles_app', '0014_auto_20201006_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observations',
            name='relevance',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
        migrations.AlterField(
            model_name='stocks',
            name='s_close',
            field=models.DecimalField(decimal_places=3, max_digits=8),
        ),
        migrations.AlterField(
            model_name='stocks',
            name='s_high',
            field=models.DecimalField(decimal_places=3, max_digits=8),
        ),
        migrations.AlterField(
            model_name='stocks',
            name='s_low',
            field=models.DecimalField(decimal_places=3, max_digits=8),
        ),
        migrations.AlterField(
            model_name='stocks',
            name='s_open',
            field=models.DecimalField(decimal_places=3, max_digits=8),
        ),
    ]
