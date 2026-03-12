from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/slots/', views.slot_list, name='slot_list'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),
]
