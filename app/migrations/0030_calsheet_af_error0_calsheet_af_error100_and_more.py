# Generated by Django 5.1.1 on 2024-10-04 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_report_date_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='calsheet',
            name='af_error0',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='af_error100',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='af_error25',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='af_error50',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='af_error75',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='al_error0',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='al_error100',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='al_error25',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='al_error50',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='calsheet',
            name='al_error75',
            field=models.FloatField(default=0),
        ),
    ]
