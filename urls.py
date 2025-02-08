from django.urls import path, include
from .api.views import PricePredictionView

urlpatterns = [
    path('api/', include('users.urls')),  # This will prefix all URLs with /api/
    path('api/predict-price/', PricePredictionView.as_view(), name='predict-price'),
] 