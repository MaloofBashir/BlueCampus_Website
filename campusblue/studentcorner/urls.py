from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name="index"),
    path('bonafide',views.bonafide,name='bonafide'),
]
