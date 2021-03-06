from django.db import models
from django.contrib.auth.models import User
import json
# Create your models here.


# class User(models.Model):
#     id = models.CharField(primary_key=True, max_length=10)
#     email = models.CharField(max_length=20)
#     name = models.CharField(max_length=30)
#     preference = models.CharField(max_length=30)

class Preference(models.Model):
    userID = models.IntegerField(default=1)
    cuisineName = models.CharField(max_length=30, default='Chinese')

    class Meta:
        unique_together = (("userID", "cuisineName"),)

    def __str__(self):
        return str(self.userID) + '-' + self.cuisineName


class CuisineType(models.Model):
    cuisineName = models.CharField(primary_key=True, max_length=30, default='Chinese')


class SharedOrder(models.Model):
    time = models.DateTimeField()
    restaurantID = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='unfulfilled')
    pickupPoint = models.CharField(max_length=100)
    # we need a new attribute 'status' to indicate whether it is fulfilled(i.e.meets min order amount)


class Order(models.Model):
    location = models.CharField(max_length=100)
    time = models.DateTimeField()
    totalCost = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    userID = models.IntegerField(default=1)
    restaurantID = models.IntegerField(default=1)
    sharedOrderID = models.ForeignKey(SharedOrder, on_delete=models.CASCADE, default=1, null=True)

    def __str__(self):
        return self.location + ' - ' + str(self.userID)


class Restaurant(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    location = models.CharField(max_length=100)
    priceRange = models.CharField(max_length=30)
    hour = models.CharField(max_length=30)
    image = models.CharField(max_length=1000, null=True)
    minOrderFee = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)

    def __str__(self):
        return self.name + ' - ' + self.type


class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    foodName = models.CharField(max_length=20)

    def __str__(self):
        return self.foodName + ' - ' + str(self.price) + ' - '


# class Include(models.Model):
#     foodName = models.CharField(max_length=20)
#     restaurantID = models.IntegerField(default=1)
#     time = models.DateTimeField()
#     orderLocation = models.CharField(max_length=100)
#     userID = models.CharField(max_length=10)
#     quantity = models.IntegerField(default=1)
#
#     class Meta:
#         unique_together = (("foodName", "restaurantID", "time", "orderLocation", "userID"),)
#
#     def __str__(self):
#         return self.foodName + ' - ' + self.userID

class Include(models.Model):
    foodID = models.IntegerField(default=1)
    orderID = models.IntegerField(default=1)
    quantity = models.IntegerField(default=1)

    # class Meta:
    #     unique_together = (("foodID", "orderID"),)

    def __str__(self):
        return str(self.foodID) + ' - ' + str(self.orderID)

