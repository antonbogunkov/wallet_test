# Generated by Django 5.1.3 on 2024-11-28 08:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Wallet",
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
                ("label", models.CharField(max_length=255, verbose_name="label")),
                (
                    "balance",
                    models.DecimalField(
                        decimal_places=18,
                        default=0,
                        max_digits=38,
                        verbose_name="balance",
                    ),
                ),
            ],
            options={
                "verbose_name": "Wallet",
                "verbose_name_plural": "Wallets",
                "ordering": ("label",),
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("balance__gte", 0)), name="balance_gte_zero"
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Transaction",
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
                ("txid", models.CharField(max_length=255, unique=True)),
                ("amount", models.DecimalField(decimal_places=18, max_digits=38)),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wallet.wallet"
                    ),
                ),
            ],
            options={
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
                "ordering": ("id",),
            },
        ),
    ]
