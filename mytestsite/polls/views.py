from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Restaurant, FoodItem, Order, Include
from .forms import SignUpForm

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
    if not request.user.is_authenticated:
        return redirect('login')
    
    data = []
    orderLocation = "blahblah street"
    orderTime = timezone.now()
    orderUser = request.user
    order = Order(location=orderLocation, time=orderTime, userID=orderUser.id, sharedOrderID=0)
    order.save()
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and request.POST[key] != '0':
            #should look up food items according to the ids here
            foodItem = FoodItem.objects.get(pk=key)
            foodName = foodItem.foodName
            foodPrice = foodItem.price
            restaurantID = foodItem.restaurant.id
            foodQuantity = int(request.POST[key])
            include = Include(foodName=foodName, restaurantID=restaurantID, time=orderTime, orderLocation=orderLocation, userID=orderUser.id, quantity=foodQuantity)
            include.save()
            data.append({'foodName':foodName, 'quantity':request.POST[key], 'price':foodPrice, 'includeId':include.id})
    return render(request, 'polls/order.html', {'orderItems':data})

def updateOrder(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        includeInstance = Include.objects.get(pk=int(request.POST['includeId']))
        includeInstance.quantity=int(request.POST['quantity'])
        includeInstance.save()
        return HttpResponse("Successful update on Include instance: "+str(includeInstance.pk))
    else:
        raise Http404

def deleteOrder(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        includeInstance = Include.objects.get(pk=int(request.POST['includeId']))
        includeInstance.delete()
        return HttpResponse("Successful deleted Include instance: "+str(request.POST['includeId']))
    else:
        raise Http404

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'polls/signup.html', {'form': form})

def orderHistory(request):
    if not request.user.is_authenticated:
        return redirect('login')
    orderUser = request.user
    orders = Order.objects.filter(userID=orderUser.id)
    return render(request, 'polls/orderHistory.html',{'orders':orders})

'''
def orderDetail(request):
    #get all food items included in the order and render 'polls/order.html' page with them
    pass
'''