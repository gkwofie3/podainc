# Generated by Django 5.1.1 on 2024-10-04 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_manuals_ext'),
    ]

    operations = [
        migrations.AddField(
            model_name='manuals',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
