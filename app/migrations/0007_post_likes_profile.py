# Generated by Django 4.0.4 on 2023-05-25 13:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_alter_user_options_alter_user_managers_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0006_delete_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="likes",
            field=models.ManyToManyField(
                related_name="likes",
                through="app.PostLike",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="images/avatar",
                        verbose_name="Avatar",
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=63, null=True)),
                ("birth_date", models.CharField(blank=True, max_length=63, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
