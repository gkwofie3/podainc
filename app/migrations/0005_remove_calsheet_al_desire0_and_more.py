# Generated by Django 5.0.4 on 2024-08-04 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_standardinstruments_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calsheet',
            name='al_desire0',
        ),
        migrations.RemoveField(
            model_name='calsheet',
            name='al_desire100',
        ),
        migrations.RemoveField(
            model_name='calsheet',
            name='al_desire25',
        ),
        migrations.RemoveField(
            model_name='calsheet',
            name='al_desire50',
        ),
        migrations.RemoveField(
            model_name='calsheet',
            name='al_desire75',
        ),
        migrations.AddField(
            model_name='calsheet',
            name='af_deviation',
            field=models.FloatField(default=0, verbose_name='As found error'),
        ),
    ]
