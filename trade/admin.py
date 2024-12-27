from django.contrib import admin

from .models import Security, TradeHistory


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    models = Security
    list_display  = (
        "id",
        "secid",
        "regnumber",
        "name",
        "emitent_title",
    )


@admin.register(TradeHistory)
class TradeHistoryAdmin(admin.ModelAdmin):
    models = TradeHistory
    list_display  = (
        "id",
        "security",
        "tradedate",
        "numtrades",
        "open",
    )
