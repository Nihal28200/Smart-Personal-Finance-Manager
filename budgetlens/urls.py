from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core App (Dashboard, Expenses, Profile)
    path('core/', include('core.urls')),
    
    # Accounts App (Login, Signup, Logout)
    path('accounts/', include('accounts.urls')),
    
    # Agar koi seedha '/' par aaye toh Dashboard par bhejo
    path('', lambda request: redirect('dashboard', permanent=False)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)