# Generated by Django 5.1.4 on 2025-01-18 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery_app', '0004_remove_painting_dimensions'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='status',
            field=models.CharField(choices=[('unpaid', 'unpaid'), ('paid', 'paid')], default='unpaid', max_length=10),
        ),
    ]
