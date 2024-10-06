# Generated by Django 5.0.4 on 2024-08-08 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_remove_admin_is_active_remove_admin_is_verified_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResetTokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=225, verbose_name='Token key')),
                ('is_used', models.BooleanField(default=False, verbose_name='Is used')),
                ('token_for', models.CharField(max_length=224, verbose_name='Created for ')),
            ],
        ),
        migrations.AlterField(
            model_name='admin',
            name='is_admin',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='admin',
            name='ppic',
            field=models.FileField(default='admins/user.jpg', upload_to='admins', verbose_name='Profile picture'),
        ),
    ]
