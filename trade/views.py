import logging

from rest_framework import status

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import F

from .serializers import SecuritySerializer, TradeHistorySerializer
from .models import Security, TradeHistory
from .services.import_data import import_securities_and_trade_history


logger = logging.getLogger(__name__)


class SecurityViewSet(ModelViewSet):
    queryset = Security.objects.all()
    serializer_class = SecuritySerializer

    @action(detail=False, methods=["get"], url_path="summary")
    def get_summary_data(self, request):
        data = (
            TradeHistory.objects.all()
            .select_related("security")
            .values(
                secid=F("security__secid"),
                regnumber=F("security__regnumber"),
                name=F("security__name"),
                emitent_title=F("security__emitent_title"),
                tradedate_annotated=F("tradedate"),
                numtrades_annotated=F("numtrades"),
                open_annotated=F("open"),
            )
        )
        logger.info("Сводные данные собраны")
        return Response(data, status=status.HTTP_200_OK)


class TradeHistoryViewSet(ModelViewSet):
    queryset = TradeHistory.objects.all()
    serializer_class = TradeHistorySerializer

    def get_queryset(self):
        security_id = self.request.query_params.get("security_id")
        if security_id:
            return self.queryset.filter(security__id=security_id)
        return super().get_queryset()


class ImportdataViewSet(ViewSet):
    @action(detail=False, methods=["post"])
    def import_data(self, request):
        import_securities_and_trade_history()

        securities = Security.objects.all()
        serializer = SecuritySerializer(securities, many=True)
        logger.info("Данные с Мос биржи собраны и сохранены в бд")

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
