from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Main entry point for the application urls
    path('', include('stkpush.urls')),
    
    # Django Admin Interface
    path('admin/', admin.site.urls),
]