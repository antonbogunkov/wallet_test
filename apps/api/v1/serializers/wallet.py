from rest_framework_json_api import serializers

from apps.wallet.models import Wallet


class WalletBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class WalletWriteSerializer(WalletBaseSerializer):
    class Meta(WalletBaseSerializer.Meta):
        read_only_fields = ("balance",)
