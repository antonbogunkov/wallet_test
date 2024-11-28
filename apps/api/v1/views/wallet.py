from rest_framework_json_api.views import ModelViewSet

from apps.api.v1.serializers import WalletBaseSerializer, WalletWriteSerializer
from apps.wallet.models import Wallet


class WalletViewSet(ModelViewSet):
    """Wallet View Set"""

    queryset = Wallet.objects.all()

    def get_serializer_class(self):
        match self.action:
            case "create" | "partial_update" | "update":
                return WalletWriteSerializer
            case "list" | "retrieve":
                return WalletBaseSerializer
