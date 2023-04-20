# Generated by Django 4.1.6 on 2023-04-19 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='rate',
            field=models.IntegerField(blank=True, choices=[(4, '80'), (2, '40'), (5, '100'), (3, '60'), (1, '20')], null=True),
        ),
    ]
