# Generated by Django 5.1.4 on 2024-12-31 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species_name', models.CharField(max_length=255)),
                ('scientific_name', models.CharField(max_length=255)),
                ('preferred_light', models.CharField(max_length=255)),
                ('ideal_temp', models.CharField(max_length=255)),
                ('bloom_time', models.CharField(max_length=255)),
                ('toxicity', models.CharField(max_length=255)),
                ('ideal_water', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='plants/')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('light', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=20)),
                ('location', models.CharField(choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TaskToCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateTimeField()),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPlant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='user_plants/')),
            ],
        ),
        migrations.CreateModel(
            name='UserPlantTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('misting', 'Misting'), ('watering', 'Watering'), ('pruning', 'Pruning'), ('fertilizing', 'Fertilizing')], max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('last_completed_at', models.DateTimeField(blank=True, null=True)),
                ('interval', models.PositiveIntegerField(default=1)),
                ('unit', models.CharField(choices=[('day', 'Day(s)'), ('week', 'Week(s)'), ('month', 'Month(s)')], default='day', max_length=50)),
            ],
        ),
    ]
