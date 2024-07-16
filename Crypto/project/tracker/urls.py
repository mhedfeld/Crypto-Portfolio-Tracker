from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path('add/', views.add_holding, name='add_holding'),
    path('delete_holding/<int:holding_id>/', views.delete_holding, name='delete_holding'),
    path('crypto/<int:crypto_id>/', views.crypto_detail, name='crypto_detail'),
    path('get_portfolio_data/', views.get_portfolio_data, name='get_portfolio_data'),
]