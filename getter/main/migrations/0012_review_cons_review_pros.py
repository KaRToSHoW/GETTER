# Generated by Django 5.1.4 on 2025-03-09 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_order_products_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='cons',
            field=models.TextField(blank=True, null=True, verbose_name='Минусы'),
        ),
        migrations.AddField(
            model_name='review',
            name='pros',
            field=models.TextField(blank=True, null=True, verbose_name='Плюсы'),
        ),
    ]
