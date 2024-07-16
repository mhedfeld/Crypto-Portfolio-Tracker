from django.db import models

# Create your models here.
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CryptoCurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=18, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class HistoricalPrice(models.Model):
    cryptocurrency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['cryptocurrency', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.price} - {self.timestamp}"

class Holding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cryptocurrency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=18, decimal_places=8)
    purchase_price = models.DecimalField(max_digits=18, decimal_places=2)
    purchase_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.cryptocurrency.symbol}: {self.quantity}"

    def get_current_value(self):
        return self.quantity * self.cryptocurrency.current_price

    def get_value_change_percentage(self):
        if self.purchase_price == 0:
            return 0
        current_price = Decimal(str(self.cryptocurrency.current_price))
        change = (current_price - self.purchase_price) / self.purchase_price * 100
        return round(change, 2)