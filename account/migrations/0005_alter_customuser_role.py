# Generated by Django 4.1 on 2023-12-17 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_customuser_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(3, 'USER'), (1, 'SUPERADMIN'), (2, 'COMPLAIN REVIEWER')], default=3),
        ),
    ]
