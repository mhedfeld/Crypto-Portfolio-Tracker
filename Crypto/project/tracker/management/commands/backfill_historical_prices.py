# management/commands/backfill_historical_prices.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tracker.models import CryptoCurrency, HistoricalPrice
from tracker.views import get_crypto_price

class Command(BaseCommand):
    help = 'Backfills historical prices for all cryptocurrencies'

    def handle(self, *args, **options):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=1825)  # 5 years

        cryptos = CryptoCurrency.objects.all()
        
        for crypto in cryptos:
            self.stdout.write(f"Backfilling prices for {crypto.name}")
            current_date = start_date
            while current_date <= end_date:
                if not HistoricalPrice.objects.filter(cryptocurrency=crypto, timestamp__date=current_date).exists():
                    price = get_crypto_price(crypto.name.lower())
                    if price > 0:
                        HistoricalPrice.objects.create(
                            cryptocurrency=crypto,
                            price=price,
                            timestamp=current_date
                        )
                current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Successfully backfilled historical prices'))