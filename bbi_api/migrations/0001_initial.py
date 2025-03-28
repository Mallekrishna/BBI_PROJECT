# Generated by Django 5.1.7 on 2025-03-25 08:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bbi_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelematicsData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('speed', models.FloatField()),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('acceleration', models.FloatField()),
                ('brake_force', models.FloatField(blank=True, null=True)),
                ('is_hard_brake', models.BooleanField(default=False)),
                ('rpm', models.IntegerField(blank=True, null=True)),
                ('fuel_level', models.FloatField(blank=True, null=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='telematics_data', to='bbi_app.driverprofile')),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['driver', '-timestamp'], name='bbi_api_tel_driver__4d21df_idx')],
            },
        ),
    ]
