from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('deals/', deals, name="deals"),

    #authentication
    path('sign-in/', sign_in, name="sign-in"),
    path('sign-up/', sign_up, name="sign-up"),
    path('customer-forget-password/', forget_Password, name='forget_Password'),
    path('account/logout/', logout_view, name="logout_view"),
    path('change-password/', change_password, name="change_password"),

    path('deals/detail/<slug:slug>/', deal_detail, name='deal_detail'),
    path('coupons/', coupons, name="coupons"),
    path('categories/', category_list, name='category_list'),
    path('profile/', customer_profile, name="customer_profile"),


    # path('login/google/', google_login_view, name='google_login')
]
