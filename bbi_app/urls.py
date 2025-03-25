from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),  
    path('upload-trip/', views.upload_trip_data, name='upload_trip'),
    path('trip/<int:trip_id>/', views.trip_details, name='trip_details'),
    path('profile/', views.profile, name='profile'),
    
]