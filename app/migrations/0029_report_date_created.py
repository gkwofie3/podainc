# Generated by Django 5.1.1 on 2024-10-03 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_report_conclusion'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='date_created',
            field=models.DateField(auto_now=True),
        ),
    ]
