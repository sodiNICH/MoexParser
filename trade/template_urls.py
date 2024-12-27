from django.urls import path

from .services import renderer_template


urlpatterns = [
    path("", renderer_template.SecurityListTemplate.as_view()),
    path("history/", renderer_template.TradeHistoryListTemplate.as_view()),
    path("summary/", renderer_template.SummaryDataListTemplate.as_view()),
]
