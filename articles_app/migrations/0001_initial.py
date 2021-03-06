# Generated by Django 3.0.3 on 2020-09-03 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stocks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market', models.CharField(max_length=100)),
                ('company_name', models.TextField()),
                ('s_open', models.DecimalField(decimal_places=2, max_digits=8)),
                ('s_high', models.DecimalField(decimal_places=2, max_digits=8)),
                ('s_low', models.DecimalField(decimal_places=2, max_digits=8)),
                ('s_close', models.DecimalField(decimal_places=2, max_digits=8)),
                ('date', models.DateTimeField()),
            ],
        ),
    ]
