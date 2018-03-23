from django.db import models
# Create your models here.


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    email = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    preference = models.CharField(max_length=30)


class Order(models.Model):
    location = models.CharField(max_length=100)
    time = models.DateTimeField()
    userID = models.CharField(max_length=10)
    sharedOrderID = models.CharField(max_length=10)

    class Meta:
        unique_together = (("location", "time", "userID"),)


class FoodItem(models.Model):
    description = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    foodName = models.CharField(max_length=20)
    restaurantName = models.CharField(max_length=30)
    restaurantLocation = models.CharField(max_length=100)

    class Meta:
        unique_together = (("foodName", "restaurantName", "restaurantLocation"),)


class Restaurant(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    location = models.CharField(max_length=100)
    priceRange = models.CharField(max_length=30)
    hour = models.DateTimeField()

    class Meta:
        unique_together = (("name", "location"),)


class Include(models.Model):
    foodName = models.CharField(max_length=20)
    restaurantName = models.CharField(max_length=30)
    restaurantLocation = models.CharField(max_length=100)
    time = models.DateTimeField()
    orderLocation = models.CharField(max_length=100)
    userID = models.CharField(max_length=10)

    class Meta:
        unique_together = (("foodName", "restaurantName", "restaurantLocation", "time", "orderLocation", "userID"),)


class SharedOrder(models.Model):
    time = models.DateTimeField()
    orderLocation = models.CharField(max_length=100)
    userID = models.CharField(max_length=10)
    pickupPoint = models.CharField(max_length=100)

    class Meta:
        unique_together = (("time", "orderLocation", "userID"),)