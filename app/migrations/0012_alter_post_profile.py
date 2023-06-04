# Generated by Django 4.0.4 on 2023-05-26 07:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0011_post_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="app.profile"
            ),
        ),
    ]
