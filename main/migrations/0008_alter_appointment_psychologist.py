# Generated by Django 5.1.1 on 2024-10-07 22:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_appointment_psychologist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='psychologist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.psychologist'),
        ),
    ]
