
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^lookdata/',views.lookdata,name='lookdata'),
    url(r'^delete',views.delete, name='delete'),
    url(r'^update',views.update, name='update'),
    url(r'^query',views.query, name='query'),
    url(r'^insert',views.insert, name='insert'),
]