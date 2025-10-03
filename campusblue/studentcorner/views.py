from django.shortcuts import render

def index(request):
    return render(request,"studentcorner/home.html")

def bonafide(request):
    return render(request,"studentcorner/bonafide.html")
