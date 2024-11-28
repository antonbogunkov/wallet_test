from decimal import Decimal

from django.test import TestCase

from apps.wallet.factories import WalletFactory

from ..serializers import (
    WalletWriteSerializer,
    WalletBaseSerializer,
    TransactionBaseSerializer,
)


class WalletSerializerTests(TestCase):
    def test_wallet_write_serializer(self):
        data = {
            "label": "Test Wallet",
            "balance": "1000.00",
        }
        serializer = WalletWriteSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        wallet = serializer.save()

        self.assertEqual(wallet.balance, Decimal("0"))

    def test_wallet_base_serializer(self):
        wallet = WalletFactory(label="Test Wallet", balance=Decimal("500.00"))
        serializer = WalletBaseSerializer(wallet)
        self.assertEqual(serializer.data["label"], "Test Wallet")
        self.assertEqual(serializer.data["balance"], "500.000000000000000000")


class TransactionSerializerTests(TestCase):
    def test_transaction_serializer(self):
        wallet = WalletFactory()
        data = {
            "wallet": {
                "type": "Wallet",
                "id": wallet.id,
            },
            "txid": "tx-serializer-test",
            "amount": "250.00",
        }
        serializer = TransactionBaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        transaction = serializer.save()
        self.assertEqual(transaction.wallet.id, wallet.id)
        self.assertEqual(transaction.txid, "tx-serializer-test")
        self.assertEqual(transaction.amount, Decimal("250.00"))
