from django.db import models
from django.utils.translation import gettext_lazy as _


class Transaction(models.Model):
    wallet = models.ForeignKey("wallet.Wallet", on_delete=models.CASCADE)
    txid = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(decimal_places=18, max_digits=38)

    class Meta:
        ordering = ("id",)
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __str__(self):
        return f"Transaction `{self.txid}` of {self.wallet}"
