# Generated by Django 4.1 on 2023-12-15 11:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_complain_assigned_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='complain',
            name='complain_video',
            field=models.FileField(blank=True, null=True, upload_to='complain-video/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov']), django.core.validators.MaxValueValidator(104857600, message='File size must be no more than 100 MB.')]),
        ),
    ]
