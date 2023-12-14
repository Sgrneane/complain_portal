# Generated by Django 4.1 on 2023-12-13 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0015_rename_complain_available_complain_assigned_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complain',
            name='complain_status',
            field=models.PositiveBigIntegerField(choices=[(1, 'Pending'), (2, 'Processing'), (3, 'Responsed'), (4, 'Rejected')], default=1),
        ),
        migrations.AlterField(
            model_name='complain',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
