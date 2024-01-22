from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('staffs_list/', staffs_list , name= 'staffs_list' ),
    path('superuser_list/', superuser_list, name='superuser_list'),
    path('users/', users, name='users'),

    #this is authentication url
    path('login/', login, name='login'),
    path('sign_up/', sign_up, name='sign_up'),
    path('logout/', login_view, name='logout'),
    path('forget-password/', forgetPassword, name='forget-password'),
    path('change-password/', changePassword, name='change-password'),
    
    path('create_staff/', create_staff, name='create_staff')
]
