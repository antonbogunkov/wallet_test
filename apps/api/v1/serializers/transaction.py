from rest_framework_json_api import serializers

from apps.wallet.models import Transaction


class TransactionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class InsufficientBalanceError(serializers.ValidationError):
    default_code = "insufficient_balance"
