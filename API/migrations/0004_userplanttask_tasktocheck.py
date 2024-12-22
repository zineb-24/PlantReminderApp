# Generated by Django 5.1.4 on 2024-12-22 12:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_alter_userplant_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPlantTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('misting', 'Misting'), ('watering', 'Watering'), ('pruning', 'Pruning'), ('fertilizing', 'Fertilizing')], max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('last_completed_at', models.DateTimeField(blank=True, null=True)),
                ('interval', models.PositiveIntegerField(default=1)),
                ('unit', models.CharField(choices=[('day', 'Day(s)'), ('week', 'Week(s)'), ('month', 'Month(s)')], default='day', max_length=50)),
                ('user_plant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='API.userplant')),
            ],
        ),
        migrations.CreateModel(
            name='TaskToCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateTimeField()),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user_plant_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.userplanttask')),
            ],
        ),
    ]
