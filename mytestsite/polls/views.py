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
    return render(request,'polls/index.html')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    # get all food types that appear in all preference relations
    # or just hard code this line
    allTypes = ['Chinese', 'Japanese', 'Korean', 'Thai', 'Breakfast and Brunch', 'Coffee']
    # TODO: get user's preference from the preference relation
    preferences = ['Chinese', 'Korean'] 
    return render(request, 'polls/profile.html',{'user':user, 'allTypes':allTypes, 'preferences':preferences})

def restaurants(request):
    allRestaurant = Restaurant.objects.all()
        
    # declare data that will be sent to front end
    filteredRestaurant = allRestaurant
    orderLocation = ""
    preferences = []
    # get all food types that appear in all preference relations 
    # or just hard code this line
    allTypes = ['Chinese', 'Japanese', 'Korean', 'Thai', 'Breakfast and Brunch', 'Coffee']
    
    # fill in data if available
    if request.user.is_authenticated:
        # TODO: get user's preference from the preference relation
        user = request.user
        preferences = ['Chinese', 'Korean'] 
        
    if request.method == "GET":
        if ("address" in request.GET) and (request.GET["address"] != "Type your address here"):
            orderLocation = request.GET["address"]
            
        #if directed here from index page
        if "foodType" in request.GET: 
            foodType = request.GET["foodType"]
            if foodType and (foodType in allTypes):
                preferences = [foodType]
        #else if directed here from restaurants page
        elif "foodTypeList" in request.GET: 
            foodTypeList = request.GET.getlist("foodTypeList")
            temp = []
            for foodType in foodTypeList:
                if foodType in allTypes:
                    temp.append(foodType)
            if temp:
                preferences = temp
        # TODO: filter restaurants here according to preferences(if exists) and order history
        # filter based on orderLocation(if exists)
        # use Python requests with Google Map API to convert street address to latitude/longitude (https://developers.google.com/maps/documentation/geocoding/intro)
        # could also install python library for geocoding library(e.g. geocoder)
        # filteredRestaurant = ...
        
    request.session["orderLocation"] = orderLocation
    return render(request, 'polls/restaurants.html', {'restaurants': filteredRestaurant, 'orderLocation': orderLocation, 'allTypes':allTypes, 'preferences':preferences})

def restaurantDetails(request):
    restaurantId = request.POST["restaurantId"]
    restaurantInfo = Restaurant.objects.filter(id=restaurantId).values()[0]
    restaurantDetail = Restaurant.objects.get(pk=restaurantId).fooditem_set.all()
    restaurantInfo['menu'] = restaurantDetail
    request.session["restaurantId"] = restaurantId
    return render(request,'polls/restaurantDetails.html', {'restaurantDetails': restaurantInfo})

def finishOrder(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    data = []
    orderLocation = ""
    if "orderLocation" in request.session:
        orderLocation = request.session["orderLocation"]
    orderTime = timezone.now()
    orderUser = request.user
    order = Order(location=orderLocation, time=orderTime, userID=orderUser.id, sharedOrderID=0)
    order.save()
    request.session["orderId"] = order.pk
    restaurantId = request.session["restaurantId"]
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and request.POST[key] != '0':
            #should look up food items according to the ids here
            foodItem = FoodItem.objects.get(pk=key)
            foodName = foodItem.foodName
            foodPrice = foodItem.price
            foodQuantity = int(request.POST[key])
            include = Include(foodName=foodName, restaurantID=restaurantId, time=orderTime, orderLocation=orderLocation, userID=orderUser.id, quantity=foodQuantity)
            include.save()
            data.append({'foodName':foodName, 'quantity':request.POST[key], 'price':foodPrice, 'includeId':include.id})
    restaurant = Restaurant.objects.get(id=restaurantId)
    return render(request, 'polls/finishOrder.html', {'orderItems':data, 'restaurantName':restaurant.name, "orderLocation":orderLocation})

def currentOrders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    currentOrders = currentOrdersHelper(user)
    return render(request, 'polls/currentOrders.html', {'currentOrders': currentOrders, 'user':user})

def currentOrdersHelper(user):
    # dummy data
    # TODO: compile data to send by finding orders which belong to unfulfilled SharedOrders and the food items included
    
    currentOrders = [
        {'id':1, 'time':'ordertimexxx', 'restaurantName':'rest name xxx', 
         'restaurantLocation': 'restaurant location ccc', 'restaurantPriceRange': 'SS', 'location': 'order location',
         'sharedOrder': 11, 'pickUpLoc': 'temp pickup loc', 'status': 'unfulfilled',
         'items': [
             {'foodName':'A', 'quantity':1, 'price': 12},
             {'foodName':'B', 'quantity':2, 'price': 9}
         ]},
        {'id':2, 'time':'ordertimeyyy', 'restaurantName':'rest name yyy', 
         'restaurantLocation': 'restaurant location ddd', 'restaurantPriceRange': 'SSS', 'location': 'order location ww',
         'sharedOrder': 12, 'pickUpLoc': 'temp pickup loc mmm', 'status': 'unfulfilled',
         'items': [
             {'foodName':'C', 'quantity':3, 'price': 2}
         ]}
    ]
    
    return currentOrders

def updateItem(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        includeInstance = Include.objects.get(pk=int(request.POST['includeId']))
        includeInstance.quantity=int(request.POST['quantity'])
        includeInstance.save()
        return HttpResponse("Successful update on Include instance: "+str(includeInstance.pk))
    else:
        raise Http404

def deleteItem(request):
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

def confirmOrder(request):
    orderId = request.session["orderId"]
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and request.POST[key] != '0':
            # TODO: update food item quantity(same as in finishOrder)
            pass
    if "orderLocation" in request.POST:
        request.session["orderLocation"] = request.POST["orderLocation"]
        # TODO: then update orderLocation in database with orderId
        
    # TODO: shared order finding/updating process goes here
    # we might also need to clean up expired unfulfilled shared orders and user orders here
    
    user = request.user
    currentOrders = currentOrdersHelper(user)
    return render(request, 'polls/currentOrders.html', {'currentOrders': currentOrders, 'user':user})

def cancelOrder(request):
    orderId = request.session["orderId"]
    Order.objects.filter(id=orderId).delete()
    # TODO: delete Include records of the food items in this order using orderId here
    
    return render(request, 'polls/index.html')

def updatePrefs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        orderUser = request.user
        newPrefs = request.POST.getlist("updatedPrefs")
        # TODO: update the preference database
        return HttpResponse("Successful updated preferences")
    else:
        raise Http404