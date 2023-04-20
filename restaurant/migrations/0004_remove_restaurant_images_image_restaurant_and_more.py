# Generated by Django 4.1.6 on 2023-04-19 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_alter_restaurant_images_alter_restaurant_rate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='images',
        ),
        migrations.AddField(
            model_name='image',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_images', to='restaurant.restaurant'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='rate',
            field=models.IntegerField(blank=True, choices=[(2, '40'), (5, '100'), (3, '60'), (4, '80'), (1, '20')], null=True),
        ),
    ]
