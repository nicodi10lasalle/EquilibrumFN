# Generated by Django 5.1.1 on 2024-11-19 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_psychologist_cover_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='feelings',
        ),
        migrations.RemoveField(
            model_name='student',
            name='note_creator',
        ),
        migrations.RemoveField(
            model_name='student',
            name='private_notes',
        ),
        migrations.RemoveField(
            model_name='student',
            name='reason',
        ),
        migrations.AddField(
            model_name='psychologist',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
        migrations.AddField(
            model_name='student',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
    ]