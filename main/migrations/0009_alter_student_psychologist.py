# Generated by Django 5.1.1 on 2024-10-21 20:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_appointment_psychologist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='psychologist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_students', to='main.psychologist'),
        ),
    ]
