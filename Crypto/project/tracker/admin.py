
from django.contrib import admin
from .models import CryptoCurrency, Holding

admin.site.register(CryptoCurrency)
admin.site.register(Holding)
