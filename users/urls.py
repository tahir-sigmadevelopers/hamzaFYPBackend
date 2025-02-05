from django.urls import path
from .views import SignupView, LoginView, UserListView, PropertyCreateView,PropertyDeleteView,PropertyDetailView,PropertyUpdateView 

urlpatterns = [
    path('property/delete/<int:id>/', PropertyDeleteView.as_view(), name='delete-property'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('properties-create/', PropertyCreateView.as_view(), name='property-create'),
    path('property/<int:id>/', PropertyDetailView.as_view(), name='edit-property'),
    path('property/update/<int:id>/', PropertyUpdateView.as_view(), name='update-property'),

]
