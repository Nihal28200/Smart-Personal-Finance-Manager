from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Signup Page (Custom View)
    path('signup/', views.signup, name='signup'),
    
    # Login Page (Django ka bana-banaya view)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # Logout Action
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]