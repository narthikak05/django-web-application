from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'), 
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Default behavior without specifying a template
    path('profile/', views.profile, name='profile'),
    path('createprofile/', views.create_profile, name='createprofile'),
    path('sellerprofile/<int:id>/', views.seller_profile, name='sellerprofile'),
]
