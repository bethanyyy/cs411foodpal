from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurantDetails/<int:id>/', views.restaurantDetails, name='restaurantDetails'),
    path('order/', views.order, name='order')
]