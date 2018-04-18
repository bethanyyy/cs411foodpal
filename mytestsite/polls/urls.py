from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurantDetails/', views.restaurantDetails, name='restaurantDetails'),
    path('login/', auth_views.login, {'template_name': 'polls/login.html'}, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('orderHistory/', views.orderHistory, name='orderHistory'),
    path('profile/',views.profile, name='profile'),
    path('finishOrder/', views.finishOrder, name='finishOrder'),
    path('finishOrder/update/', views.updateItem, name='updateItem'),
    path('finishOrder/delete/', views.deleteItem, name='deleteItem'),
    path('currentOrders/', views.currentOrders, name='currentOrders'),
    path('confirmOrder/', views.confirmOrder, name='confirmOrder'),
    path('cancelOrder/', views.cancelOrder, name='cancelOrder'),
    path('profile/updatePrefs/', views.updatePrefs, name='updatePrefs')
]