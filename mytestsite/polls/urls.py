from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurantDetails/<int:id>/', views.restaurantDetails, name='restaurantDetails'),
    path('order/', views.order, name='order'),
    path('order/update/', views.updateOrder, name='updateOrder'),
    path('order/delete/', views.deleteOrder, name='deleteOrder'),
    path('login/', auth_views.login, {'template_name': 'polls/login.html'}, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('orderHistory/', views.orderHistory, name='orderHistory')
    #path('orderDetail/', views.orderDetail, name='orderDetail')
]