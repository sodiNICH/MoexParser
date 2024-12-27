from django.views.generic import TemplateView

class SecurityListTemplate(TemplateView):
    template_name = "securities.html"


class TradeHistoryListTemplate(TemplateView):
    template_name = "trade_history.html"


class SummaryDataListTemplate(TemplateView):
    template_name = "summary.html"
