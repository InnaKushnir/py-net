# Generated by Django 4.0.4 on 2023-05-26 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0013_postlike_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="postlike",
            name="status",
            field=models.CharField(
                choices=[("LIKE", "Like"), ("UNLIKE", "Unlike")], max_length=10
            ),
        ),
    ]
