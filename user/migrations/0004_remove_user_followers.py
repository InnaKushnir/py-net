# Generated by Django 4.0.4 on 2023-05-25 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_user_followers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='followers',
        ),
    ]
