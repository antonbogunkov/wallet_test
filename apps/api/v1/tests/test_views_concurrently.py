import threading
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from apps.wallet.factories import WalletFactory

from .utils import ObjectFromDict


class WalletConcurrentTransactionTests(APITransactionTestCase):
    start_balance = Decimal("1000.00")
    threads_count = 10

    def setUp(self):
        self.wallet = WalletFactory(balance=self.start_balance)

    def test_concurrent_transactions(self):
        def make_transaction(txid, amount):
            data = ObjectFromDict(
                "Transaction",
                {
                    "wallet": self.wallet,
                    "txid": txid,
                    "amount": str(amount),
                },
            )
            return self.client.post(
                reverse("api:v1:transaction-list"), data, format=settings.JSON_FORMAT
            )

        bad_amount = Decimal("-100000.00")
        amounts = (
            Decimal("100.00"),
            Decimal("-150.00"),
            Decimal("250.00"),
            Decimal("-300.00"),
            Decimal("450.37"),
            bad_amount,
            Decimal("-100.12"),
            Decimal("250.00"),
            Decimal("-300.00"),
            Decimal("450.37"),
            Decimal("-100.12"),
        )

        transactions_data = {
            f"tx-create-test-{i}": amt for i, amt in enumerate(amounts)
        }

        threads = []
        responses = []

        for txid, amount in transactions_data.items():
            thread = threading.Thread(
                target=lambda tid, amt: responses.append(make_transaction(tid, amt)),
                args=(txid, amount),
            )
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.wallet.refresh_from_db()

        good_responses = []
        bad_responses = []
        for response in responses:
            if response.status_code == status.HTTP_201_CREATED:
                good_responses.append(response)
            else:
                bad_responses.append(response)

        self.assertEqual(len(good_responses), len(amounts) - 1)
        self.assertEqual(len(bad_responses), 1)

        expected_balance = (
            self.start_balance + sum(transactions_data.values()) - bad_amount
        )
        self.assertEqual(self.wallet.balance, expected_balance)
