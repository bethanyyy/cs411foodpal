from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

from .models import Restaurant, FoodItem, Order, Include, Preference, SharedOrder
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
    # TODO: get user's preference from the preference relation - clear
    profileUserID = user.id
    preferences = Preference.objects.filter(userID=profileUserID).values_list('cuisineName', flat=True)
    return render(request, 'polls/profile.html',{'user':user, 'allTypes':allTypes, 'preferences':preferences})


def restaurants(request):
    allRestaurant = Restaurant.objects
        
    # declare data that will be sent to front end
    filteredRestaurant = allRestaurant.all()
    orderLocation = ""
    preferences = []
    # get all food types that appear in all preference relations 
    # or just hard code this line
    allTypes = ['Chinese', 'Japanese', 'Korean', 'Thai', 'Breakfast and Brunch', 'Coffee']
    
    # fill in data if available
    if request.user.is_authenticated:
        # TODO: get user's preference from the preference relation - clear
        user = request.user
        profileUserID = user.id
        preferences = Preference.objects.filter(userID=profileUserID).values_list('cuisineName', flat=True)
        
    if request.method == "GET":
        if ("orderLocation" in request.GET) and (request.GET["orderLocation"] != "Type your address here"):
            orderLocation = request.GET["orderLocation"]
            
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
        # TODO: filter restaurants here according to preferences(if exists) and order history - clear
        if (preferences):
            filteredRestaurant = allRestaurant.none()
            for pref in preferences:
                resultRestaurant = allRestaurant.filter(type=pref)
                filteredRestaurant = filteredRestaurant | resultRestaurant
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
    restaurantId = request.session["restaurantId"]
    order = Order.objects.create(location=orderLocation, time=orderTime, totalCost=0.00, userID=orderUser.id, restaurantID=restaurantId, sharedOrderID_id=None)
    order.save()
    request.session["orderId"] = order.pk

    # TODO: display total cost
    orderTotalCost = 0.00
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and request.POST[key] != '0':
            #should look up food items according to the ids here
            foodItem = FoodItem.objects.get(pk=key)
            foodName = foodItem.foodName
            foodId = foodItem.id
            foodPrice = foodItem.price
            foodQuantity = int(request.POST[key])
            orderTotalCost += float(foodPrice) * foodQuantity
            include = Include(foodID=foodId, orderID=order.pk, quantity=foodQuantity)
            include.save()
            data.append({'foodName':foodName, 'quantity':request.POST[key], 'price':foodPrice, 'includeId':include.id, 'foodId':foodId})
    order.totalCost = Decimal(orderTotalCost)
    order.save()
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
    # TODO: compile data to send by finding orders which belong to unfulfilled SharedOrders and the food items included - clear

    currentOrders = []

    idx = 0
    allUserOrders = Order.objects.filter(userID=user.id).all()
    for userOrder in allUserOrders:
        sharedOrder = userOrder.sharedOrderID
        if sharedOrder is not None and sharedOrder.status == "unfulfilled":
            idx += 1
            restaurant = Restaurant.objects.get(pk=userOrder.restaurantID)
            restaurantName = restaurant.name
            restaurantLocation = restaurant.location
            restaurantPriceRange = restaurant.priceRange

            orderLocation = userOrder.location
            orderId = userOrder.id
            foodItems = []
            includeInstances = Include.objects.filter(orderID=orderId)
            for includeInstance in includeInstances:
                food = FoodItem.objects.get(pk=includeInstance.foodID)
                foodItem = {'foodName':food.foodName, 'quantity':includeInstance.quantity, 'price': food.price}
                foodItems.append(foodItem)

            sharedOrderNum = sharedOrder.id
            pickUpLoc = sharedOrder.pickupPoint
            sharedOrderStatus = sharedOrder.status
            curOrder = {'id':idx, 'time':userOrder.time, 'restaurantName':restaurantName,
                        'restaurantLocation': restaurantLocation, 'restaurantPriceRange': restaurantPriceRange, 'location': orderLocation,
                        'sharedOrder': sharedOrderNum, 'pickUpLoc': pickUpLoc, 'status': sharedOrderStatus,
                        'items': foodItems}
            currentOrders.append(curOrder)
    
    return currentOrders


def updateItem(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        includeInstance = Include.objects.get(pk=int(request.POST['includeId']))
        originalQuantity = includeInstance.quantity
        includeInstance.quantity=int(request.POST['quantity'])
        includeInstance.save()

        order = Order.objects.get(id=includeInstance.orderID)
        print(order)
        orderTotalCost = float(order.totalCost)
        foodPrice = FoodItem.objects.get(pk=includeInstance.foodID).price
        orderTotalCost -= float(foodPrice) * float(originalQuantity)
        orderTotalCost += float(foodPrice) * includeInstance.quantity
        order.totalCost = Decimal(orderTotalCost)
        order.save()

        return HttpResponse("Successful update on Include instance: "+str(includeInstance.pk))
    else:
        raise Http404


def deleteItem(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        includeInstance = Include.objects.get(pk=int(request.POST['includeId']))
        originalQuantity = includeInstance.quantity
        includeInstance.delete()

        order = Order.objects.get(id=includeInstance.orderID)
        orderTotalCost = float(order.totalCost)
        foodPrice = FoodItem.objects.get(pk=includeInstance.foodID).price
        orderTotalCost -= float(foodPrice) * float(originalQuantity)
        order.totalCost = Decimal(orderTotalCost)
        order.save()

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
    orderTotalCost = 0.00
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and key != "orderLocation" and request.POST[key] != '0':
            # TODO: update food item quantity(same as in finishOrder) - clear
            includeInstance = Include.objects.get(id=key)
            includeInstance.quantity = int(request.POST[key])
            includeInstance.save()

            order = Order.objects.get(id=orderId)
            foodPrice = FoodItem.objects.get(pk=includeInstance.foodID).price
            orderTotalCost += float(foodPrice) * includeInstance.quantity
            order.totalCost = Decimal(orderTotalCost)
            order.save()
            pass
    if "orderLocation" in request.POST:
        request.session["orderLocation"] = request.POST["orderLocation"]
        print(request.POST["orderLocation"])
        # TODO: then update orderLocation in database with orderId - clear
        order = Order.objects.get(id=orderId)
        order.location = request.POST["orderLocation"]
        order.save()
    # TODO: shared order finding/updating process goes here - calculate distance and fulfill status
    # we might also need to clean up expired unfulfilled shared orders and user orders here

    orderSaved = False
    allSharedOrders = SharedOrder.objects.all()
    selectedSharedOrder = None
    for curSharedOrder in allSharedOrders:
        if curSharedOrder.status == "unfulfilled" and \
                curSharedOrder.restaurantID == order.restaurantID and \
                calculateDistance(curSharedOrder, order):

            calculateMidPt(curSharedOrder, order)

            selectedSharedOrder = curSharedOrder
            order.sharedOrderID = curSharedOrder
            order.save()
            orderSaved = True
            break
    if not orderSaved:
        newSharedOrder = SharedOrder(time='2006-10-25 14:30:59', restaurantID=order.restaurantID, status="unfulfilled", pickupPoint=order.location)
        newSharedOrder.save()
        selectedSharedOrder = newSharedOrder
        order.sharedOrderID = newSharedOrder
        order.save()
        orderSaved = True

    checkMinOrderFee(selectedSharedOrder)

    user = request.user
    currentOrders = currentOrdersHelper(user)
    return render(request, 'polls/currentOrders.html', {'currentOrders': currentOrders, 'user':user})


def calculateMidPt(sharedOrder, newOrder):
    geolocator = Nominatim()
    curPickupPoint = geolocator.geocode(sharedOrder.pickupPoint)
    curPickupLoc = (curPickupPoint.latitude, curPickupPoint.longitude)
    newOrderAddr = geolocator.geocode(newOrder.location)
    newOrderLoc = (newOrderAddr.latitude, newOrderAddr.longitude)

    centerLat = 0.5 * (curPickupPoint.latitude + newOrderAddr.latitude)
    centerLong = 0.5 * (curPickupPoint.longitude + newOrderAddr.longitude)

    center = str(centerLat) + ", " + str(centerLong)
    centerLoc = geolocator.reverse(center)

    sharedOrder.pickupPoint = centerLoc.address
    sharedOrder.save()


def calculateDistance(sharedOrder, newOrder):
    geolocator = Nominatim()
    curPickupPoint = geolocator.geocode(sharedOrder.pickupPoint)
    curPickupLoc = (curPickupPoint.latitude, curPickupPoint.longitude)
    newOrderAddr = geolocator.geocode(newOrder.location)
    newOrderLoc = (newOrderAddr.latitude, newOrderAddr.longitude)

    print(curPickupLoc)
    print(newOrderLoc)
    distance = vincenty(curPickupLoc, newOrderLoc).miles
    print("distance")
    print(distance)
    if distance < 4.0:
        return True


def checkMinOrderFee(sharedOrder):
    restaurant = Restaurant.objects.get(pk=sharedOrder.restaurantID)
    currentTotal = 0
    for order in sharedOrder.order_set.all():
        currentTotal += order.totalCost
    if currentTotal >= restaurant.minOrderFee:
        sharedOrder.status = "fulfilled"
        sharedOrder.save()

def cancelOrder(request):
    orderId = request.session["orderId"]
    Order.objects.filter(id=orderId).delete()
    # TODO: delete Include records of the food items in this order using orderId here - clear
    Include.objects.filter(orderID=orderId).delete()
    return render(request, 'polls/index.html')


def updatePrefs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        orderUser = request.user
        newPrefs = request.POST.getlist("updatedPrefs[]")
        # TODO: update the preference database - clear
        orderUserID = orderUser.id
        Preference.objects.filter(userID=orderUserID).delete()
        for newPref in newPrefs:
            preference = Preference(userID=orderUserID, cuisineName=newPref)
            preference.save()
        return HttpResponse("Successful updated preferences")
    else:
        raise Http404