from django.urls import path
from .api.views import PricePredictionView

urlpatterns = [
    # ... other urls ...
    path('api/predict-price/', PricePredictionView.as_view(), name='predict-price'),
] 