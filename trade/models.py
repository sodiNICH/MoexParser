from django.db import models


class Security(models.Model):
    secid = models.CharField(max_length=20)
    regnumber = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=255)
    emitent_title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}-{self.secid}"


class TradeHistory(models.Model):
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name="trade_history")
    tradedate = models.DateField()
    numtrades = models.IntegerField()
    open = models.FloatField(null=True)

    def __str__(self):
        return f"History for {self.numtrades} on {self.tradedate}"
