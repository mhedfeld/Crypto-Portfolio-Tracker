from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from .models import Holding, CryptoCurrency, HistoricalPrice
from .forms import HoldingForm
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.db.models import Avg
from django.http import JsonResponse
from django.db.models import Min, Max
import json 


cg = CoinGeckoAPI()

def update_crypto_prices():
    from .models import CryptoCurrency, HistoricalPrice  # Import here to avoid circular import
    cryptos = CryptoCurrency.objects.all()
    for crypto in cryptos:
        price = get_crypto_price(crypto.name.lower())
        if price > 0:
            crypto.current_price = price
            crypto.save()
            try:
                HistoricalPrice.objects.create(cryptocurrency=crypto, price=price)
            except Exception as e:
                print(f"Error creating HistoricalPrice for {crypto.name}: {e}")

cg = CoinGeckoAPI()

def get_crypto_price(crypto_id):
    cache_key = f'crypto_price_{crypto_id}'
    cached_price = cache.get(cache_key)
    
    if cached_price is None:
        try:
            data = cg.get_price(ids=crypto_id, vs_currencies='usd')
            if data and crypto_id in data:
                price = Decimal(str(data[crypto_id]['usd']))
                cache.set(cache_key, price, 300)  # Cache for 5 minutes
                return price
        except Exception as e:
            print(f"Error fetching price for {crypto_id}: {e}")
    
    return cached_price or Decimal('0')

def update_crypto_prices():
    cryptos = CryptoCurrency.objects.all()
    for crypto in cryptos:
        price = get_crypto_price(crypto.name.lower())
        if price > 0:
            crypto.current_price = price
            crypto.save()
            try:
                HistoricalPrice.objects.create(cryptocurrency=crypto, price=price)
            except Exception as e:
                print(f"Error creating HistoricalPrice for {crypto.name}: {e}")

def get_portfolio_history(user, start_date, end_date):
    dates = []
    values = []
    holdings = Holding.objects.filter(user=user).select_related('cryptocurrency')
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        daily_value = Decimal('0')
        for holding in holdings:
            historical_price = HistoricalPrice.objects.filter(
                cryptocurrency=holding.cryptocurrency,
                timestamp__date=current_date
            ).order_by('-timestamp').first()
            
            if historical_price:
                daily_value += holding.quantity * historical_price.price
            else:
                daily_value += holding.quantity * holding.cryptocurrency.current_price
        
        values.append(float(daily_value))
        current_date += timedelta(days=1)
    
    return dates, values

@cache_page(60 * 5)  # Cache the portfolio view for 5 minutes
@login_required
def portfolio(request):
    holdings = Holding.objects.filter(user=request.user).select_related('cryptocurrency')
    total_value = sum(holding.quantity * holding.cryptocurrency.current_price for holding in holdings)

    # Get 7-day data for initial chart
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    dates, values = get_portfolio_history(request.user, start_date, end_date)

    for holding in holdings:
        holding.current_value = holding.quantity * holding.cryptocurrency.current_price
        if holding.purchase_price > 0:
            holding.value_change_percentage = ((holding.cryptocurrency.current_price - holding.purchase_price) / holding.purchase_price) * 100
        else:
            holding.value_change_percentage = 0

    context = {
        'holdings': holdings,
        'total_value': total_value,
        'chart_dates': json.dumps(dates),
        'chart_values': json.dumps(values),
    }
    return render(request, 'tracker/portfolio.html', context)

@login_required
def get_portfolio_data(request):
    period = request.GET.get('period', '7d')
    end_date = timezone.now().date()
    
    if period == '7d':
        start_date = end_date - timedelta(days=6)
    elif period == '1m':
        start_date = end_date - timedelta(days=29)
    elif period == '5m':
        start_date = end_date - timedelta(days=149)
    elif period == '1y':
        start_date = end_date - timedelta(days=364)
    elif period == '5y':
        start_date = end_date - timedelta(days=1824)
    else:
        start_date = end_date - timedelta(days=6)

    dates, values = get_portfolio_history(request.user, start_date, end_date)
    return JsonResponse({'dates': dates, 'values': values})
    
@login_required
def add_holding(request):
    if request.method == 'POST':
        form = HoldingForm(request.POST)
        if form.is_valid():
            holding = form.save(commit=False)
            holding.user = request.user
            holding.save()
            messages.success(request, 'New holding added successfully!')
            return redirect('portfolio')
    else:
        form = HoldingForm()
    return render(request, 'tracker/add_holding.html', {'form': form})


@login_required
def delete_holding(request, holding_id):
    holding = get_object_or_404(Holding, id=holding_id, user=request.user)
    if request.method == 'POST':
        holding.delete()
        messages.success(request, f"Holding for {holding.cryptocurrency.name} has been deleted.")
        cache.delete(f'portfolio_{request.user.id}')  # Invalidate user's portfolio cache
    return redirect('portfolio')



@cache_page(60 * 15)  # Cache the crypto detail view for 15 minutes
@login_required
def crypto_detail(request, crypto_id):
    crypto = get_object_or_404(CryptoCurrency, id=crypto_id)
    
    # Fetch historical data (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    cache_key = f'crypto_history_{crypto_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        try:
            historical_data = cg.get_coin_market_chart_range_by_id(
                id=crypto.name.lower(),
                vs_currency='usd',
                from_timestamp=int(start_date.timestamp()),
                to_timestamp=int(end_date.timestamp())
            )

            prices = historical_data['prices']
            
            # Format data for Chart.js
            labels = [datetime.fromtimestamp(price[0]/1000).strftime('%Y-%m-%d') for price in prices]
            data = [price[1] for price in prices]

            # Convert to JSON for use in JavaScript
            labels_json = json.dumps(labels)
            data_json = json.dumps(data)
            
            cached_data = {'labels': labels_json, 'data': data_json}
            cache.set(cache_key, cached_data, 60 * 15)  # Cache for 15 minutes
        except Exception as e:
            # Handle any API errors
            print(f"Error fetching data: {e}")
            cached_data = {'labels': '[]', 'data': '[]'}
    
    return render(request, 'tracker/crypto_detail.html', {
        'crypto': crypto,
        'labels': cached_data['labels'],
        'data': cached_data['data']
    })