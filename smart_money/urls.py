from django.urls import path
from .views import RetailHistoryTrades
urlpatterns = [
    path('', RetailHistoryTrades.as_view(), name='historyOfRetailTrades'),

]