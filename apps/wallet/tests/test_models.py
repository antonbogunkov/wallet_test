from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from apps.wallet.models import Wallet, Transaction


class WalletModelTests(TestCase):
    def test_wallet_creation(self):
        wallet = Wallet.objects.create(label="Test Wallet")
        self.assertEqual(wallet.label, "Test Wallet")
        self.assertEqual(wallet.balance, Decimal("0"))
        self.assertEqual(str(wallet), "Wallet `Test Wallet`")

    def test_wallet_str_method(self):
        wallet = Wallet.objects.create(label="My Wallet")
        self.assertEqual(str(wallet), "Wallet `My Wallet`")

    def test_wallet_balance_constraint(self):
        wallet = Wallet(label="Negative Balance Wallet", balance=Decimal("-100.00"))
        with self.assertRaises(IntegrityError):
            wallet.save()

    def test_wallet_meta_ordering(self):
        wallet1 = Wallet.objects.create(label="B Wallet")
        wallet2 = Wallet.objects.create(label="A Wallet")
        wallets = Wallet.objects.all()
        self.assertEqual(wallets[0], wallet2)
        self.assertEqual(wallets[1], wallet1)


class TransactionModelTests(TestCase):
    def setUp(self):
        self.wallet = Wallet.objects.create(label="Test Wallet")

    def test_transaction_creation(self):
        tx = Transaction.objects.create(
            wallet=self.wallet, txid="tx12345", amount=Decimal("100.00")
        )
        self.assertEqual(tx.wallet, self.wallet)
        self.assertEqual(tx.txid, "tx12345")
        self.assertEqual(tx.amount, Decimal("100.00"))
        self.assertEqual(str(tx), f"Transaction `tx12345` of {self.wallet}")

    def test_transaction_str_method(self):
        tx = Transaction.objects.create(
            wallet=self.wallet, txid="tx67890", amount=Decimal("50.00")
        )
        self.assertEqual(str(tx), f"Transaction `tx67890` of {self.wallet}")

    def test_transaction_unique_txid(self):
        Transaction.objects.create(
            wallet=self.wallet, txid="unique_txid", amount=Decimal("10.00")
        )
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(
                wallet=self.wallet, txid="unique_txid", amount=Decimal("20.00")
            )

    def test_transaction_amount_precision(self):
        precise_amount = Decimal("1.123456789012345678")
        tx = Transaction.objects.create(
            wallet=self.wallet, txid="tx_precision", amount=precise_amount
        )
        self.assertEqual(tx.amount, precise_amount)

    def test_transaction_wallet_relation(self):
        tx = Transaction.objects.create(
            wallet=self.wallet, txid="tx_wallet_relation", amount=Decimal("30.00")
        )
        self.assertEqual(tx.wallet, self.wallet)

    def test_transaction_meta_ordering(self):
        tx1 = Transaction.objects.create(
            wallet=self.wallet, txid="tx1", amount=Decimal("10.00")
        )
        tx2 = Transaction.objects.create(
            wallet=self.wallet, txid="tx2", amount=Decimal("20.00")
        )
        transactions = Transaction.objects.all()
        self.assertEqual(transactions[0], tx1)
        self.assertEqual(transactions[1], tx2)

    def test_transaction_foreign_key_on_delete(self):
        Transaction.objects.create(
            wallet=self.wallet, txid="tx_foreign_key", amount=Decimal("15.00")
        )
        self.wallet.delete()
        transactions = Transaction.objects.filter(txid="tx_foreign_key")
        self.assertEqual(transactions.count(), 0)
