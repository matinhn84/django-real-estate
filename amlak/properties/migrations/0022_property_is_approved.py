# Generated by Django 5.1.4 on 2025-01-21 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0021_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
