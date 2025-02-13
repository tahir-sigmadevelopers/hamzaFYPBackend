from django.urls import path, include
from .api.views import PricePredictionView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/', include('users.urls')),  # This will prefix all URLs with /api/
    path('api/predict-price/', PricePredictionView.as_view(), name='predict-price'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 