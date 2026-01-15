from django.urls import path
from stkpush import views

app_name = 'stkpush'

urlpatterns = [
    path('', views.home, name='home'),
    path('token/', views.token, name='token'),
    path('pay/', views.pay, name='pay'),
    path('stk/', views.stk, name='stk'),
    path('callback/', views.callback, name='callback'),
    path('check-status/', views.check_status, name='check_status'),
]