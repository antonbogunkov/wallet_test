from django.contrib import admin

from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "balance")
    search_fields = ("label",)
    readonly_fields = ("balance",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = ("wallet_label", "txid")
    list_display = ("wallet__label", "txid", "amount")
    list_select_related = ("wallet",)
    readonly_fields = ("amount",)
