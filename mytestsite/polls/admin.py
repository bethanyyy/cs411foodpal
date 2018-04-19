from django.contrib import admin
from .models import FoodItem, Restaurant, Order, Include, CuisineType, Preference, SharedOrder

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(Include)
admin.site.register(CuisineType)
admin.site.register(Preference)
admin.site.register(SharedOrder)