from django.db import transaction, IntegrityError
from rest_framework_json_api.views import ModelViewSet

from apps.api.v1.serializers import (
    TransactionBaseSerializer,
    InsufficientBalanceError,
)
from apps.wallet.models import Transaction, Wallet


class TransactionViewSet(ModelViewSet):
    """Transaction View Set"""

    queryset = Transaction.objects.all()
    serializer_class = TransactionBaseSerializer

    def perform_create(self, serializer):
        target_wallet = serializer.validated_data["wallet"]

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=target_wallet.pk)
            wallet.balance += serializer.validated_data["amount"]
            try:
                wallet.save()
            except IntegrityError as error:
                raise InsufficientBalanceError(detail=error.args[1]) from error

        return super().perform_create(serializer)

    def perform_update(self, serializer):
        current_wallet = serializer.instance.wallet
        target_wallet = serializer.validated_data.get("wallet") or current_wallet
        amount = serializer.validated_data.get("amount") or serializer.instance.amount

        with transaction.atomic():
            wallets = Wallet.objects.select_for_update().filter(
                pk__in=[current_wallet.pk, target_wallet.pk]
            )
            old_wallet = new_wallet = wallets.get(pk=current_wallet.pk)
            if current_wallet.pk != target_wallet.pk:
                new_wallet = wallets.get(pk=target_wallet.pk)

            old_wallet.balance -= serializer.instance.amount
            new_wallet.balance += amount

            try:
                old_wallet.save()
                new_wallet.save()
            except IntegrityError as error:
                raise InsufficientBalanceError(detail=error.args[1]) from error

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        target_wallet = instance.wallet

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=target_wallet.pk)
            wallet.balance -= instance.amount
            try:
                wallet.save()
            except IntegrityError as error:
                raise InsufficientBalanceError(detail=error.args[1]) from error

        return super().perform_destroy(instance)
