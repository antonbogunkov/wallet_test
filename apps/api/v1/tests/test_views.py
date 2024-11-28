from django.conf import settings
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from decimal import Decimal
from django.urls import reverse

from apps.wallet.models import Transaction, Wallet
from apps.wallet.factories import WalletFactory, TransactionFactory

from .utils import ObjectFromDict


class WalletCreateAPITestCase(APITransactionTestCase):
    url = reverse("api:v1:wallet-list")

    def test_create_wallet_failed(self):
        response = self.client.post(self.url, None, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, {}, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.url, {"data": None}, format=settings.JSON_FORMAT
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, {"data": {}}, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_wallet_success(self):
        data = ObjectFromDict(
            "Wallet",
            {
                "label": "Test Wallet",
            },
        )
        response = self.client.post(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["balance"]), 0)

    def test_create_wallet_balance_zero(self):
        data = ObjectFromDict(
            "Wallet",
            {
                "label": "Test Wallet",
                "balance": Decimal(1000000),
            },
        )
        response = self.client.post(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["balance"]), 0)


class WalletUpdateAPITestCase(APITransactionTestCase):
    def setUp(self):
        self.wallet = WalletFactory(balance=Decimal("500.00"))
        self.url = reverse("api:v1:wallet-detail", kwargs={"pk": self.wallet.id})

    def test_update_wallet_failed(self):
        response = self.client.patch(
            self.url, {"data": None}, format=settings.JSON_FORMAT
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(
            self.url, {"data": {}}, format=settings.JSON_FORMAT
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_update_wallet_success(self):
        response = self.client.patch(self.url, None, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = ObjectFromDict(
            "Wallet",
            {
                "id": self.wallet.id,
                "label": self.wallet.label + "1",
            },
        )
        response = self.client.patch(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], self.wallet.label + "1")
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.label, response.data["label"])

    def test_update_wallet_balance(self):
        data = ObjectFromDict(
            "Wallet",
            {
                "id": self.wallet.id,
                "balance": "1000.00",
            },
        )
        response = self.client.patch(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data["balance"]), Decimal("500.00"))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_delete_wallet(self):
        response = self.client.delete(self.url, None, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Wallet.objects.count(), 0)

        response = self.client.delete(self.url, None, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TransactionCreateAPITests(APITransactionTestCase):
    url = reverse("api:v1:transaction-list")

    def setUp(self):
        self.wallet = WalletFactory(balance=Decimal("1000.00"))

    def test_create_transaction_failed(self):
        response = self.client.post(self.url, None, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, {}, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.url, {"data": None}, format=settings.JSON_FORMAT
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, {"data": {}}, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_transaction_success(self):
        initial_balance = self.wallet.balance
        amount = Decimal("200.00")
        data = ObjectFromDict(
            "Transaction",
            {
                "wallet": self.wallet,
                "txid": "tx-create-test",
                "amount": str(amount),
            },
        )
        response = self.client.post(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        transaction = Transaction.objects.get(txid="tx-create-test")
        self.assertEqual(transaction.amount, amount)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, initial_balance + amount)

    def test_create_transaction_insufficient_balance(self):
        amount = Decimal("-1200.00")
        data = ObjectFromDict(
            "Transaction",
            {
                "wallet": self.wallet,
                "txid": "tx-create-test",
                "amount": str(amount),
            },
        )
        response = self.client.post(
            reverse("api:v1:transaction-list"), data, format=settings.JSON_FORMAT
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("insufficient_balance", response.data[0]["code"])


class TransactionUpdateAPITests(APITransactionTestCase):
    def setUp(self):
        self.wallet = WalletFactory(balance=Decimal("1000.00"))
        self.transaction = TransactionFactory(
            wallet=self.wallet, amount=Decimal("1000.00")
        )

        self.url = reverse(
            "api:v1:transaction-detail", kwargs={"pk": self.transaction.id}
        )

    def test_delete_transaction(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(id=self.transaction.id).exists())
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("0.00"))

    def test_update_transaction_txid(self):
        new_txid = self.transaction.txid + "1"
        data = ObjectFromDict(
            "Transaction", {"id": self.transaction.id, "txid": new_txid}
        )
        response = self.client.patch(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.txid, new_txid)

    def test_update_transaction_wallet(self):
        new_wallet = WalletFactory(balance=Decimal("0.00"))
        data = ObjectFromDict(
            "Transaction", {"id": self.transaction.id, "wallet": new_wallet}
        )
        response = self.client.patch(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.wallet.refresh_from_db()
        new_wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("0.00"))
        self.assertEqual(new_wallet.balance, self.transaction.amount)

    def test_update_transaction_amount(self):
        new_amount = Decimal("200.00")
        data = ObjectFromDict(
            "Transaction", {"id": self.transaction.id, "amount": str(new_amount)}
        )
        response = self.client.patch(self.url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, new_amount)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, new_amount)


class TransactionUpdateInsufficientAPITests(APITransactionTestCase):
    base_url = "api:v1:transaction-detail"

    def setUp(self):
        self.wallet = WalletFactory(balance=Decimal("100.00"))

        self.transaction1 = TransactionFactory(
            wallet=self.wallet, amount=Decimal("1100.00")
        )
        self.transaction2 = TransactionFactory(
            wallet=self.wallet, amount=Decimal("-1000.00")
        )

    def test_delete_transaction(self):
        url = reverse(self.base_url, kwargs={"pk": self.transaction1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("insufficient_balance", response.data[0]["code"])

    def test_update_transaction_amount(self):
        url = reverse(self.base_url, kwargs={"pk": self.transaction1.id})

        data = ObjectFromDict(
            "Transaction",
            {"id": self.transaction1.id, "amount": str(Decimal("899.99"))},
        )
        response = self.client.patch(url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("insufficient_balance", response.data[0]["code"])

        data = ObjectFromDict(
            "Transaction",
            {"id": self.transaction1.id, "amount": str(Decimal("1000.01"))},
        )
        response = self.client.patch(url, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("0.01"))

    def test_update_transaction_wallet(self):
        url1 = reverse(self.base_url, kwargs={"pk": self.transaction1.id})
        url2 = reverse(self.base_url, kwargs={"pk": self.transaction2.id})

        wallet = WalletFactory(balance=Decimal("100.00"))
        data = ObjectFromDict(
            "Transaction", {"id": self.transaction1.id, "wallet": wallet}
        )
        response = self.client.patch(url1, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("insufficient_balance", response.data[0]["code"])

        data = ObjectFromDict(
            "Transaction", {"id": self.transaction2.id, "wallet": wallet}
        )
        response = self.client.patch(url2, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("insufficient_balance", response.data[0]["code"])

        wallet.balance = Decimal("1000")
        wallet.save()
        response = self.client.patch(url2, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("0"))

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("1100.00"))

        data = ObjectFromDict(
            "Transaction", {"id": self.transaction1.id, "wallet": wallet}
        )
        response = self.client.patch(url1, data, format=settings.JSON_FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("1100"))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("0"))
