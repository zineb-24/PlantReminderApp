# Generated by Django 5.1.4 on 2024-12-31 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='bloom_time',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
