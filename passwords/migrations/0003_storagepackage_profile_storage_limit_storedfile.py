# Generated by Django 5.1 on 2024-08-26 12:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("passwords", "0002_profile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StoragePackage",
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
                ("name", models.CharField(max_length=100)),
                ("storage_limit", models.IntegerField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.AddField(
            model_name="profile",
            name="storage_limit",
            field=models.IntegerField(default=1000000000),
        ),
        migrations.CreateModel(
            name="StoredFile",
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
                ("file", models.FileField(upload_to="user_files")),
                (
                    "file_type",
                    models.CharField(
                        choices=[
                            ("photo", "Photo"),
                            ("document", "Document"),
                            ("music", "Music"),
                            ("other", "Other"),
                        ],
                        max_length=10,
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("comment", models.TextField(blank=True)),
                (
                    "shared_with",
                    models.ManyToManyField(
                        blank=True,
                        related_name="shared_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
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
