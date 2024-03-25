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
    path('profile/', management_profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),

    #this is authentication url
    path('login/', login, name='login'),
    path('sign_up/', superuser_required(sign_up), name='sign_up'),
    path('logout/', logout_view, name='logout'),
    path('forget-password/', forgetPassword, name='forget-password'),
    path('change-password/<token>/', changePassword, name='change-password'),
    path('verify_account/', login_verify, name='verify_account'),
    
    path('create_staff/', superuser_required(create_staff), name='create_staff'),
    path('create_superuser/', superuser_required(create_superuser), name='create_superuser'),

    #recourse
    path('category/', category, name='category'),
    path('sub-category/', subCategory, name="subCategory"),
    path('brand-list/', brand_list, name= "brand_list" ),
    path('deal-list/', deal_list, name='deal_list'),
    path('add-category/', add_category, name='add_category'),
    path('add-sub-category/', add_subCategory, name='add_subCategory'),
    path('add-brand/', add_brand, name='add_brand'),
    path('add-deal', add_deal, name='add_deal'),


]
