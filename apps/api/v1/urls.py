from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .schema import urls as schema_urls
from .views import (
    TransactionViewSet,
    WalletViewSet,
)

app_name = "v1"

router = DefaultRouter()
router.register(r"wallets", WalletViewSet)
router.register(r"transactions", TransactionViewSet)

urlpatterns = router.urls + [
    path("schema/", include(schema_urls), name="schema"),
]
