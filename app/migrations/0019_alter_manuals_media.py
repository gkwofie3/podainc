# Generated by Django 5.0.4 on 2024-08-11 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_manuals_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuals',
            name='media',
            field=models.FileField(blank=True, upload_to='manuals'),
        ),
    ]
