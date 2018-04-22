from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from django.db import connection, transaction
from itertools import chain
import datetime

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
    # SQL
    cursor = connection.cursor()
    preferences = cursor.execute('SELECT cuisineName FROM polls_preference WHERE userID = %s', [profileUserID])
    preferences = [item[0] for item in cursor.fetchall()]
    cursor.close()
    return render(request, 'polls/profile.html',{'user':user, 'allTypes':allTypes, 'preferences':preferences})


def restaurants(request):
    allRestaurant = Restaurant.objects
        
    # declare data that will be sent to front end
    filteredRestaurant = allRestaurant.raw('SELECT * FROM polls_restaurant')
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
        # SQL
        cursor = connection.cursor()
        preferences = cursor.execute('SELECT cuisineName FROM polls_preference WHERE userID = %s', [profileUserID])
        preferences = [item[0] for item in cursor.fetchall()]
        cursor.close()
        
    if request.method == "GET":
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
            prefFilteredRestaurant = allRestaurant.none()
            for pref in preferences:
                # SQL
                resultRestaurant = allRestaurant.extra(where=['type = %s'], params=[pref])
                prefFilteredRestaurant = prefFilteredRestaurant | resultRestaurant
            if ("orderLocation" in request.GET) and (request.GET["orderLocation"] != "Type your address here") and (request.GET["orderLocation"] != ""):
                filteredRestaurant = []
                orderLocation = request.GET["orderLocation"]
                geolocator = Nominatim()
                orderAddr = geolocator.geocode(orderLocation)
                if (orderAddr != None):
                    orderLoc = (orderAddr.latitude, orderAddr.longitude)
                    for restaurant in prefFilteredRestaurant:
                        restaurantAddr = geolocator.geocode(restaurant.location)
                        restaurantLoc = (restaurantAddr.latitude, restaurantAddr.longitude)
                        if vincenty(restaurantLoc, orderLoc).miles < 5.00:
                            filteredRestaurant.append(restaurant)
                emptyRest = Restaurant.objects.none()
                filteredRestaurant = list(chain(emptyRest, filteredRestaurant))
                # filteredRestaurant = filterRestaurants(request.GET["orderLocation"], prefFilteredRestaurant)
            else:
                filteredRestaurant = prefFilteredRestaurant
        elif ("orderLocation" in request.GET) and (request.GET["orderLocation"] != "Type your address here") and (request.GET["orderLocation"] != ""):
            allRestaurantList = allRestaurant.raw('SELECT * FROM polls_restaurant')
            filteredRestaurant = []
            geolocator = Nominatim()
            orderAddr = geolocator.geocode(orderLocation)
            if (orderAddr != None):
                orderLoc = (orderAddr.latitude, orderAddr.longitude)
                for restaurant in allRestaurantList:
                    restaurantAddr = geolocator.geocode(restaurant.location)
                    restaurantLoc = (restaurantAddr.latitude, restaurantAddr.longitude)
                    if vincenty(restaurantLoc, orderLoc).miles < 5.00:
                        filteredRestaurant.append(restaurant)
            emptyRest = Restaurant.objects.none()
            filteredRestaurant = list(chain(emptyRest, filteredRestaurant))
            # filteredRestaurant = filterRestaurants(request.GET["orderLocation"], allRestaurantList)
        
    request.session["orderLocation"] = orderLocation
    return render(request, 'polls/restaurants.html', {'restaurants': filteredRestaurant, 'orderLocation': orderLocation, 'allTypes':allTypes, 'preferences':preferences})


# def filterRestaurants(orderLocation, filterRange):
#     filteredRestaurant = []
#     geolocator = Nominatim()
#     orderAddr = geolocator.geocode(orderLocation)
#     if (orderAddr != None):
#         orderLoc = (orderAddr.latitude, orderAddr.longitude)
#         for restaurant in filterRange:
#             restaurantAddr = geolocator.geocode(restaurant.location)
#             restaurantLoc = (restaurantAddr.latitude, restaurantAddr.longitude)
#             if vincenty(restaurantLoc, orderLoc).miles < 5.00:
#                 filteredRestaurant.append(restaurant)
#     emptyRest = Restaurant.objects.none()
#     filteredRestaurant = list(chain(emptyRest, filteredRestaurant))
#     return filteredRestaurant


def restaurantDetails(request):
    restaurantId = request.POST["restaurantId"]

    cursor = connection.cursor()
    restaurantInfo = cursor.execute('SELECT * FROM polls_restaurant WHERE id = %s', [restaurantId])
    restaurantInfo = dictfetchall(cursor)[0]
    cursor.close()

    cursor = connection.cursor()
    restaurantDetail = dictfetchall(cursor.execute('SELECT * FROM polls_fooditem WHERE restaurant_id = %s', [restaurantId]))
    cursor.close()

    restaurantInfo['menu'] = restaurantDetail
    request.session["restaurantId"] = restaurantId
    return render(request,'polls/restaurantDetails.html', {'restaurantDetails': restaurantInfo})


def finishOrder(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    data = []
    orderLocation = ""
    orderTotal = 0.00
    if "orderLocation" in request.session:
        orderLocation = request.session["orderLocation"]
    orderTime = timezone.now()
    orderUser = request.user
    restaurantId = request.session["restaurantId"]

    cursor = connection.cursor()
    cursor.execute('INSERT INTO polls_order(location, time, totalCost, userID, restaurantID) VALUES(%s, %s, %s, %s, %s)', [orderLocation, orderTime, orderTotal, orderUser.id, restaurantId])
    transaction.commit()

    newOrderId = cursor.lastrowid
    request.session["orderId"] = cursor.lastrowid

    # TODO: display total cost
    orderTotalCost = 0.00
    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and request.POST[key] != '0':
            #should look up food items according to the ids here
            foodItem = FoodItem.objects.raw('SELECT * FROM polls_fooditem WHERE id = %s', [key])[0]
            foodName = foodItem.foodName
            foodId = foodItem.id
            foodPrice = foodItem.price
            foodQuantity = int(request.POST[key])
            orderTotalCost += float(foodPrice) * foodQuantity

            cursor.execute('INSERT INTO polls_include(foodID, orderID, quantity) VALUES(%s, %s, %s)', [foodId, newOrderId, foodQuantity])
            data.append({'foodName':foodName, 'quantity':request.POST[key], 'price':foodPrice, 'includeId':cursor.lastrowid, 'foodId':foodId})

    cursor.execute('UPDATE polls_order SET totalCost = %s WHERE id = %s', [Decimal(orderTotalCost), newOrderId])

    orderRestaurantName = cursor.execute('SELECT polls_restaurant.name FROM polls_restaurant WHERE id = %s', [restaurantId]).fetchall()[0][0]
    cursor.close()
    return render(request, 'polls/finishOrder.html', {'orderItems':data, 'restaurantName':orderRestaurantName, "orderLocation":orderLocation})


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

    # SQL
    # allUserOrders = Order.objects.filter(userID=user.id).all()
    allUserOrders = Order.objects.raw('SELECT * FROM polls_order WHERE userID = %s', [user.id])
    for userOrder in allUserOrders:
        sharedOrder = userOrder.sharedOrderID
        # only display orders made within the last hour
        curOrder = {}
        if sharedOrder is not None and (timezone.now() - sharedOrder.time).total_seconds() < 3600.0:
            curOrder = getOrderInfo(userOrder)
            currentOrders.append(curOrder)
    return sorted(currentOrders, reverse=True, key = lambda temp: temp['time'])


def getOrderInfo(userOrder):
    sharedOrder = userOrder.sharedOrderID

    restaurant = Restaurant.objects.raw('SELECT * FROM polls_restaurant WHERE id = %s', [userOrder.restaurantID])[0]
    restaurantName = restaurant.name
    restaurantLocation = restaurant.location
    minOrderFee = restaurant.minOrderFee

    orderLocation = userOrder.location
    orderUrl = orderLocation.strip().replace(' ','+')
    orderId = userOrder.id
    foodItems = []

    includeInstances = Include.objects.raw('SELECT * FROM polls_include WHERE orderID = %s', [orderId])
    for includeInstance in includeInstances:
        food = FoodItem.objects.raw('SELECT * FROM polls_fooditem WHERE id = %s', [includeInstance.foodID])[0]
        totalPrice = food.price*includeInstance.quantity
        foodItem = {'foodName':food.foodName, 'quantity':includeInstance.quantity, 'price': food.price, 'totalPrice': totalPrice}
        foodItems.append(foodItem)

    sharedOrderNum = sharedOrder.id
    pickUpLoc = sharedOrder.pickupPoint
    pickUpUrl = pickUpLoc.strip().replace(' ','+')
    sharedOrderStatus = sharedOrder.status
    curOrder = {'time':userOrder.time, 'restaurantName':restaurantName,
                'restaurantLocation': restaurantLocation, 'minOrderFee': minOrderFee, 'location': orderLocation,
                'sharedOrder': sharedOrderNum, 'pickUpLoc': pickUpLoc, 'status': sharedOrderStatus,
                'items': foodItems, 'orderTotal':userOrder.totalCost, 'orderUrl':orderUrl, 'pickUpUrl':pickUpUrl}
    return curOrder
    

def updateItem(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        # SQL
        # includeInstance = Include.objects.get(pk=int(request.POST['includeId']))
        includeInstance = Include.objects.raw('SELECT * FROM polls_include WHERE id = %s', [int(request.POST['includeId'])])[0]
        originalQuantity = includeInstance.quantity

        cursor = connection.cursor()
        cursor.execute('UPDATE polls_include SET quantity = %s WHERE id = %s', [int(request.POST['quantity']), int(request.POST['includeId'])])
        cursor.close()

        foodPrice = FoodItem.objects.raw('SELECT * FROM polls_fooditem WHERE id = %s', [includeInstance.foodID])[0].price

        costDeducted = float(foodPrice) * float(originalQuantity)
        costAdded = float(foodPrice) * int(request.POST['quantity'])
        cursor = connection.cursor()
        cursor.execute('UPDATE polls_order SET totalCost = totalCost - %s + %s WHERE id = %s', [costDeducted, costAdded, includeInstance.orderID])
        cursor.close()

        return HttpResponse("Successful update on Include instance: "+str(includeInstance.pk))
    else:
        raise Http404


def deleteItem(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        cursor = connection.cursor()
        deleteOrderInfo = cursor.execute('SELECT polls_fooditem.price * polls_include.quantity, polls_include.orderID FROM polls_fooditem, polls_include WHERE '
                             'polls_fooditem.id = polls_include.foodID AND polls_include.id = %s', [int(request.POST['includeId'])]).fetchall()
        cursor.close()
        (costDeducted, orderId) = deleteOrderInfo[0]

        cursor = connection.cursor()
        cursor.execute('DELETE FROM polls_include WHERE id = %s', [int(request.POST['includeId'])])
        cursor.close()

        cursor = connection.cursor()
        cursor.execute('UPDATE polls_order SET totalCost = totalCost - %s WHERE id = %s', [costDeducted, orderId])
        cursor.close()

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
    # SQL
    # orders = Order.objects.filter(userID=orderUser.id)
    orders = Order.objects.raw('SELECT * FROM polls_order WHERE userID = %s', [orderUser.id])
    return render(request, 'polls/orderHistory.html',{'orders':sorted(orders, reverse=True, key=lambda temp:temp.time)})


def orderDetails(request, orderId):
    curOrder = getOrderInfo(Order.objects.get(id=orderId))
    return render(request, 'polls/orderDetails.html',{'order':curOrder})


def confirmOrder(request):
    orderId = request.session["orderId"]
    order = Order.objects.raw('SELECT * FROM polls_order WHERE id = %s', [orderId])[0]
    orderTotalCost = 0.00
    cursor = connection.cursor()
    cursor.execute('UPDATE polls_order SET totalCost = %s WHERE id = %s', [Decimal(orderTotalCost), orderId])
    cursor.close()

    for key in request.POST:
        if  key != "csrfmiddlewaretoken" and key != "orderLocation" and request.POST[key] != '0':
            # TODO: update food item quantity(same as in finishOrder) - clear
            includeInstance = Include.objects.raw('SELECT * FROM polls_include WHERE id = %s', [key])[0]
            # originalQuantity = includeInstance.quantity

            cursor = connection.cursor()
            cursor.execute('UPDATE polls_include SET quantity = %s WHERE id = %s', [int(request.POST[key]), key])
            cursor.close()

            foodPrice = FoodItem.objects.raw('SELECT * FROM polls_fooditem WHERE id = %s', [includeInstance.foodID])[0].price

            costAdded = float(foodPrice) * int(request.POST[key])
            cursor = connection.cursor()
            cursor.execute('UPDATE polls_order SET totalCost = totalCost + %s WHERE id = %s', [costAdded, orderId])
            cursor.close()
            
    if "orderLocation" in request.POST:
        request.session["orderLocation"] = request.POST["orderLocation"]
        print(request.POST["orderLocation"])
        # TODO: then update orderLocation in database with orderId - clear
        cursor = connection.cursor()
        cursor.execute('UPDATE polls_order SET location = %s WHERE id = %s', [request.POST["orderLocation"], orderId])
        cursor.close()
        order = Order.objects.raw('SELECT * FROM polls_order WHERE id = %s', [orderId])[0]

    # TODO: shared order finding/updating process goes here - clear
    # we might also need to clean up expired unfulfilled shared orders and user orders here

    orderSaved = False
    allSharedOrders = SharedOrder.objects.raw('SELECT * FROM polls_sharedorder')
    selectedSharedOrder = None
    for curSharedOrder in allSharedOrders:
        if curSharedOrder.status == "unfulfilled":
            if (timezone.now() - curSharedOrder.time).total_seconds() > 3600.0:
                # curSharedOrder.status = "expired"
                # # SQL
                # curSharedOrder.save()
                cursor = connection.cursor()
                cursor.execute('UPDATE polls_sharedorder SET status = "expired" WHERE id = %s', [curSharedOrder.id])
                cursor.close()
            elif curSharedOrder.restaurantID == order.restaurantID and calculateDistance(curSharedOrder, order):
                calculateMidPt(curSharedOrder, order)

                selectedSharedOrder = curSharedOrder

                cursor = connection.cursor()
                cursor.execute('UPDATE polls_order SET sharedOrderID_id = %s WHERE id = %s', [curSharedOrder.id, order.id])
                cursor.close()
                orderSaved = True
                break
                
    if not orderSaved:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO polls_sharedorder(time, restaurantID, status, pickupPoint) VALUES(%s, %s, "unfulfilled", %s)',[timezone.now(), order.restaurantID, order.location])
        cursor.close()

        selectedSharedOrder = SharedOrder.objects.raw('SELECT * FROM polls_sharedorder WHERE id = %s', [cursor.lastrowid])[0]

        cursor = connection.cursor()
        cursor.execute('UPDATE polls_order SET sharedOrderID_id = %s WHERE id = %s', [selectedSharedOrder.id, order.id])
        cursor.close()
        orderSaved = True

    checkMinOrderFee(selectedSharedOrder)

    user = request.user
    currentOrders = currentOrdersHelper(user)
    return render(request, 'polls/currentOrders.html', {'currentOrders': currentOrders, 'user':user})


def calculateMidPt(sharedOrder, newOrder):
    geolocator = Nominatim()
    newOrderAddr = geolocator.geocode(newOrder.location)
    centerLat = newOrderAddr.latitude
    centerLong = newOrderAddr.longitude
    orderCount = 1.0
    for order in sharedOrder.order_set.all():
        orderAddr = geolocator.geocode(order.location)
        centerLat += orderAddr.latitude
        centerLong += orderAddr.longitude
        orderCount += 1.0
    
    centerLat = centerLat/orderCount
    centerLong = centerLong/orderCount


    center = str(centerLat) + ", " + str(centerLong)
    centerLoc = geolocator.reverse(center)

    cursor = connection.cursor()
    cursor.execute('UPDATE polls_sharedorder SET pickupPoint = %s WHERE id = %s', [centerLoc.address, sharedOrder.id])
    cursor.close()


def calculateDistance(sharedOrder, newOrder):
    geolocator = Nominatim()
    curPickupPoint = geolocator.geocode(sharedOrder.pickupPoint)
    curPickupLoc = (curPickupPoint.latitude, curPickupPoint.longitude)
    newOrderAddr = geolocator.geocode(newOrder.location)
    newOrderLoc = (newOrderAddr.latitude, newOrderAddr.longitude)

    distance = vincenty(curPickupLoc, newOrderLoc).miles
    if distance < 2.0:
        return True
    else:
        return False

def checkMinOrderFee(sharedOrder):
    restaurant = Restaurant.objects.raw('SELECT * FROM polls_restaurant WHERE id = %s', [sharedOrder.restaurantID])[0]
    cursor = connection.cursor()
    currentTotal = cursor.execute('SELECT SUM(totalCost) FROM polls_order GROUP BY sharedOrderID_id HAVING sharedOrderID_id = %s', [sharedOrder.id]).fetchall()[0][0]
    cursor.close()
    if currentTotal >= float(restaurant.minOrderFee):
        cursor = connection.cursor()
        cursor.execute('UPDATE polls_sharedorder SET status = "fulfilled" WHERE id = %s', [sharedOrder.id])
        cursor.close()

def cancelOrder(request):
    orderId = request.session["orderId"]
    cursor = connection.cursor()
    cursor.execute('DELETE FROM polls_order WHERE id = %s', [orderId])
    cursor.close()
    # TODO: delete Include records of the food items in this order using orderId here - clear
    cursor = connection.cursor()
    cursor.execute('DELETE FROM polls_include WHERE orderID = %s', [orderId])
    cursor.close()
    return render(request, 'polls/index.html')


def updatePrefs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        orderUser = request.user
        newPrefs = request.POST.getlist("updatedPrefs[]")
        # TODO: update the preference database - clear
        orderUserID = orderUser.id
        cursor = connection.cursor()
        cursor.execute('DELETE FROM polls_preference WHERE userID = %s', [orderUserID])
        cursor.close()
        for newPref in newPrefs:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO polls_preference(userID, cuisineName) VALUES(%s, %s)', [orderUserID, newPref])
            cursor.close()
        return HttpResponse("Successful updated preferences")
    else:
        raise Http404


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]