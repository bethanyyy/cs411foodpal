from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.shortcuts import render
def home(request):
    return render(request,'polls/home.html')
def lookdata(request):
    return render(request,'polls/lookdata.html',{'content':['testaaa','sdfdasfsaf']})

