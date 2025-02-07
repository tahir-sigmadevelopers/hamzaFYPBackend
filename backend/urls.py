"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from users.views import hello_world, PropertyCreateView , PropertyDeleteView,PropertyDetailView,PropertyUpdateView,get_properties, PricePredictionView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', hello_world),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/auth/properties-create/', PropertyCreateView.as_view(), name='property-create'),
    path('properties/', get_properties, name='get_properties'),
    path('property/delete/<int:id>/', PropertyDeleteView.as_view(), name='delete-property'),
    path('property/edit/<int:id>/', PropertyDetailView.as_view(), name='edit-property'),
    path('property/update/<int:id>/', PropertyUpdateView.as_view(), name='update-property'),
    path('api/predict-price/', PricePredictionView.as_view(), name='predict-price'),


]

urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
