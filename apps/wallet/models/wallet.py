from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    label = models.CharField(verbose_name=_("label"), max_length=255)
    balance = models.DecimalField(
        verbose_name=_("balance"),
        decimal_places=18,
        max_digits=38,
        default=0,
    )

    class Meta:
        ordering = ("label",)
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")

        constraints = [
            models.constraints.CheckConstraint(
                condition=Q(balance__gte=0),
                name="balance_gte_zero",
            ),
        ]

    def __str__(self):
        return f"Wallet `{self.label}`"
