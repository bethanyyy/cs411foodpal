from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.shortcuts import render

def home(request):
    return render(request,'polls/home.html')

def restaurants(request):
    return render(request, 'polls/restaurants.html', {
        'restaurants':[
            {'name':'Chopstix', 'type':'Chinese', 'location':'202 E Green', 'priceRange':'$$', 'hour':'4PM-3AM', 'image':'https://s3-media1.fl.yelpcdn.com/bphoto/pcfq177Gx3yQEvL5SzoMxg/o.jpg', 'id':1},
            {'name':'Kofusion', 'type':'Korean', 'location':'701 S Gregory', 'priceRange':'$$', 'hour':'11AM-9:30PM', 'image':'https://s3-media2.fl.yelpcdn.com/bphoto/ai0eukB8ZCqjUFiYl4KNjA/o.jpg', 'id':2},
            {'name':'Bangkok Thai', 'type':'Thai', 'location':'410 E Green', 'priceRange':'$', 'hour':'11AM-9PM', 'image':'https://s3-media2.fl.yelpcdn.com/bphoto/p2NjZ1qsAeDlvH6YN9FISA/o.jpg', 'id':3},
            {'name':'Cracked the Egg Came First', 'type':'Breakfast and Brunch', 'location':'619 E Green', 'priceRange':'$', 'hour':'8AM-4PM', 'image':'https://s3-media1.fl.yelpcdn.com/bphoto/LmujjLvO64Bnud93s9mu6g/o.jpg', 'id':4}
        ]
    })

def restaurantDetails(request, id):
    return render(request,'polls/restaurantDetails.html', {
        'restaurantDetails':{
            'name':'Kofusion',
            'id':id,
            'type':'Japanese', 'location':'403 E Green', 'priceRange':'$$$', 'hour':'11:30AM-2PM, 5PM-12:30AM', 'image':'https://s3-media4.fl.yelpcdn.com/bphoto/isAlSf4uNTKuXRY4T-t88g/o.jpg',
            'menu':[
                {'foodName':'Sushi sampler', 'price':6, 'description':'Try 1 of each (big, creamy, Cali, coconut, dynamite, popper)', 'id':1},
                {'foodName':'Stir fry', 'price':9, 'description':'Fresh mixed vegetables and protein tossed in our wok, your way.', 'id':2},
                {'foodName':'Spicy Korean Chicken', 'price':9, 'description':'Korean style fried chicken tossed in a sweet and spicy sauce. Served with rice.', 'id':3},
                {'foodName':'Hwe Dup Bap', 'price':17, 'description':'Spicy sashimi rice bowl. Mixed greens, rice, salmon, tuna, yellowtail, tomago, spicy crab, cucumber, apple, masago and spicy sauce. Served with miso soup.', 'id':4}
            ]
        }
    })

def order(request):
    data = []
    for key in request.POST:
        if  key != "csrfmiddlewaretoken":
            #should look up food items according to the ids here
            data.append({'id':key, 'quantity':request.POST[key], 'price':10})
    return render(request, 'polls/order.html', {'orderItems':data})
