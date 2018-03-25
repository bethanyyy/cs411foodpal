from django.shortcuts import render
from django.utils import timezone
from .models import Restaurant, FoodItem, Order, Include

# Create your views here.


def home(request):
    return render(request,'polls/home.html')


def restaurants(request):
    allRestaurant = Restaurant.objects.all()
    return render(request, 'polls/restaurants.html', {'restaurants': allRestaurant})


def restaurantDetails(request, id):
    restaurantInfo = Restaurant.objects.filter(id=id).values()[0]
    restaurantDetail = Restaurant.objects.get(pk=id).fooditem_set.all()
    restaurantInfo['menu'] = restaurantDetail
    return render(request,'polls/restaurantDetails.html', {'restaurantDetails': restaurantInfo})


def order(request):
    data = []
    orderLocation = "blahblah street"
    orderTime = timezone.now()
    orderUser = 1
    order = Order(location=orderLocation, time=orderTime, userID=orderUser, sharedOrderID=0)
    order.save()
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and request.POST[key] != '0':
            #should look up food items according to the ids here
            foodItem = FoodItem.objects.get(pk=key)
            foodName = foodItem.foodName
            foodPrice = foodItem.price
            restaurantID = foodItem.restaurant.id
            foodQuantity = int(request.POST[key])
            data.append({'foodName':foodName, 'quantity':foodQuantity, 'price':foodPrice})
            include = Include(foodName=foodName, restaurantID=restaurantID, time=orderTime, orderLocation=orderLocation, userID=orderUser, quantity=foodQuantity)
            include.save()
    return render(request, 'polls/order.html', {'orderItems':data})
