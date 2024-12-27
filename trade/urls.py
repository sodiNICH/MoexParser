from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(
    r"api/v1/security",
    views.SecurityViewSet,
    basename="security-api",
)
router.register(
    r"api/v1/history",
    views.TradeHistoryViewSet,
    basename="history-api",
)
router.register(
    r"api/v1",
    views.ImportdataViewSet,
    basename="import_data-api"
)


urlpatterns = [
    path("", include(router.urls))
]
