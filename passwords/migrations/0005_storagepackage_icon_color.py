# Generated by Django 5.1 on 2024-08-26 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("passwords", "0004_alter_storedfile_file_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="storagepackage",
            name="icon_color",
            field=models.CharField(default="#000000", max_length=7),
        ),
    ]