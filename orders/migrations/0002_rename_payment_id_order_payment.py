# Generated by Django 4.2.4 on 2023-12-16 19:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="payment_id",
            new_name="payment",
        ),
    ]
