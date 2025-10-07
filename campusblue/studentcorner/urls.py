from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name="index"),
    path('bonafide',views.bonafide_certificate,name='bonafide_certificate'),
    path('bonafide/download/<int:certificate_id>/', views.download_bonafide_pdf, name='download_bonafide_pdf'),
    path('statistics/', views.student_statistics, name='student_statistics'),

]
