from django.urls import path
from stkpush import views

app_name = 'stkpush'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Page to demonstrate Token Generation
    path('token/', views.token, name='token'),
    
    # Page to demonstrate STK Push payment
    path('pay/', views.pay, name='pay'),
    
    # Alias for the payment page
    path('stk/', views.stk, name='stk'),
    
    # Callback URL - This is the endpoint Safaricom hits with transaction results
    path('callback/', views.callback, name='callback'),
    
    # API endpoint for the frontend to poll transaction status
    path('check-status/', views.check_status, name='check_status'),
]
