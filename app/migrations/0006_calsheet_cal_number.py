# Generated by Django 5.0.4 on 2024-08-04 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_calsheet_al_desire0_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='calsheet',
            name='cal_number',
            field=models.IntegerField(default=1),
        ),
    ]
