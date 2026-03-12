from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.google_oauth_start, name='oauth_start'),
    path('callback/', views.google_oauth_callback, name='oauth_callback'),
]
