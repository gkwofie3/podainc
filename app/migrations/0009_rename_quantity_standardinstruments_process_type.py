# Generated by Django 5.0.4 on 2024-08-05 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_rename_calibration_date_calsheet_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='standardinstruments',
            old_name='quantity',
            new_name='process_type',
        ),
    ]
