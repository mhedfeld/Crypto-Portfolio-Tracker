from django.core.management.base import BaseCommand
from tracker.views import update_crypto_prices

class Command(BaseCommand):
    help = 'Updates cryptocurrency prices and stores historical data'

    def handle(self, *args, **options):
        update_crypto_prices()
        self.stdout.write(self.style.SUCCESS('Successfully updated crypto prices'))