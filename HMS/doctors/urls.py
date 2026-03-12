from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('slots/add/', views.add_slot, name='add_slot'),
    path('slots/<int:pk>/edit/', views.edit_slot, name='edit_slot'),
    path('slots/<int:pk>/delete/', views.delete_slot, name='delete_slot'),
]
