# Generated by Django 5.1.4 on 2025-04-02 18:13

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_review_cons_review_pros'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата поступления'),
        ),
    ]
