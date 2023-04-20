# Generated by Django 4.1.6 on 2023-04-20 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0004_remove_restaurant_images_image_restaurant_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='restaurant_images'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='rate',
            field=models.IntegerField(blank=True, choices=[(3, '60'), (5, '100'), (4, '80'), (1, '20'), (2, '40')], null=True),
        ),
    ]
