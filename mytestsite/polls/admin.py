from django.contrib import admin
from .models import FoodItem, Restaurant, Order, Include

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(Include)