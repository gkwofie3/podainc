# Generated by Django 5.0.4 on 2024-08-06 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_rename_quantity_standardinstruments_process_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='standardinstruments',
            name='due_cal_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='standardinstruments',
            name='last_cal_date',
            field=models.DateField(),
        ),
    ]
