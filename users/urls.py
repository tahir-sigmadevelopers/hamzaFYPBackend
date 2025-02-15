from django.urls import path
from .views import (SignupView, LoginView, UserListView, PropertyCreateView,
                   PropertyDeleteView, PropertyDetailView, PropertyUpdateView, 
                   PlaceBidView, PropertyBidsView, BidActionView, AllBidsView,
                   UserBidsView, MarkBidNotifiedView, UserStatsView,
                   UserRoleToggleView, UserDeleteView)

urlpatterns = [
    # Authentication URLs
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    
    # Property URLs
    path('properties-create/', PropertyCreateView.as_view(), name='property-create'),
    path('property/<int:id>/', PropertyDetailView.as_view(), name='property-detail'),
    path('property/update/<int:id>/', PropertyUpdateView.as_view(), name='property-update'),
    path('property/delete/<int:id>/', PropertyDeleteView.as_view(), name='delete-property'),
    
    # Bidding URLs
    path('bids/', PlaceBidView.as_view(), name='place-bid'),
    path('property/<int:property_id>/bids/', PropertyBidsView.as_view(), name='property-bids'),
    path('bids/all/', AllBidsView.as_view(), name='all-bids'),
    path('bids/<int:bid_id>/<str:action>/', BidActionView.as_view(), name='bid-action'),
    path('bids/user/<str:email>/', UserBidsView.as_view(), name='user-bids'),
    path('bids/<int:bid_id>/mark-notified/', MarkBidNotifiedView.as_view(), name='mark-bid-notified'),
    path('users/stats/', UserStatsView.as_view(), name='user-stats'),
    path('users/<int:user_id>/toggle-role/', UserRoleToggleView.as_view(), name='user-toggle-role'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user-delete'),
]
