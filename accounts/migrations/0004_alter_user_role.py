# Generated by Django 4.2.4 on 2023-08-27 08:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                blank=True, choices=[(1, "Vendor"), (2, "Customer")], null=True
            ),
        ),
    ]
