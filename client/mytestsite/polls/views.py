from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.shortcuts import render
from .forms import DeleteForm,InsertForm,UpdateForm,QueryForm
def home(request):
    return render(request,'polls/home.html')
def lookdata(request):
    return render(request,'polls/lookdata.html',{'content':['testaaa','sdfdasfsaf']})

def delete(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DeleteForm(request.POST)
        # check whether it's valid:
        print(form)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            return render(request, 'polls/delete.html', {'deleteddata': form.cleaned_data['delete']})
            # redirect to a new URL:
            return HttpResponseRedirect('/success/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = DeleteForm()

    return render(request, 'polls/delete.html', {'form': form})
def insert(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InsertForm(request.POST)
        # check whether it's valid:
        print(form)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            return render(request, 'polls/insert.html', {'insertdata': form.cleaned_data['insert']})
            # redirect to a new URL:
            return HttpResponseRedirect('/success/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = InsertForm()

    return render(request, 'polls/insert.html', {'form': form})
def query(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QueryForm(request.POST)
        # check whether it's valid:
        print(form)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            return render(request, 'polls/query.html', {'querydata': form.cleaned_data['query']})
            # redirect to a new URL:
            return HttpResponseRedirect('/success/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = QueryForm()
        return
    return render(request, 'polls/query.html', {'form': form})
def update(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UpdateForm(request.POST)
        # check whether it's valid:
        print(form)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            return render(request, 'polls/update.html', {'updatedata': form.cleaned_data['update']})
            # redirect to a new URL:
            return HttpResponseRedirect('/success/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = UpdateForm()

    return render(request, 'polls/update.html', {'form': form})