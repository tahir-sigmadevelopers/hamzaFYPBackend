from django.urls import path
from .views import (SignupView, LoginView, UserListView, PropertyCreateView,
                   PropertyDeleteView, PropertyDetailView, PropertyUpdateView, 
                   PlaceBidView, PropertyBidsView, BidActionView,AllBidsView)

urlpatterns = [
    # Authentication URLs
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    
    # Property URLs
    path('properties-create/', PropertyCreateView.as_view(), name='property-create'),
    path('property/delete/<int:id>/', PropertyDeleteView.as_view(), name='delete-property'),
    path('property/update/<int:id>/', PropertyUpdateView.as_view(), name='update-property'),
    path('property/<int:id>/', PropertyDetailView.as_view(), name='property-detail'),
    
    # Bidding URLs
    path('bids/', PlaceBidView.as_view(), name='place-bid'),
    path('property/<int:property_id>/bids/', PropertyBidsView.as_view(), name='property-bids'),
    path('bids/<int:bid_id>/accept/', BidActionView.as_view(), {'action': 'accept'}, name='accept-bid'),
    path('bids/<int:bid_id>/reject/', BidActionView.as_view(), {'action': 'reject'}, name='reject-bid'),
    path('bids/all/', AllBidsView.as_view(), name='all-bids'),

]
