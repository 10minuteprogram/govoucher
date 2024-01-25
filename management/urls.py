from django.urls import path
from .views import *
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import render

def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request,'404.html')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


urlpatterns = [
    path('', home, name='home'),
    path('staffs_list/',superuser_required(staffs_list) , name= 'staffs_list' ),
    path('superuser_list/',superuser_required(superuser_list), name='superuser_list'),
    path('users/', users, name='users'),

    #this is authentication url
    path('login/', login, name='login'),
    path('sign_up/', superuser_required(sign_up), name='sign_up'),
    path('logout/', logout_view, name='logout'),
    path('forget-password/', forgetPassword, name='forget-password'),
    path('change-password/<token>/', changePassword, name='change-password'),
    path('verify_account/', login_verify, name='verify_account'),
    
    path('create_staff/', superuser_required(create_staff), name='create_staff'),
]
