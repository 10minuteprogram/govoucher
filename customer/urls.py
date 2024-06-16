from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('deals/', deals, name="deals"),
    path('sign-in/', sign_in, name="sign-in"),
    path('sign-up/', sign_up, name="sign-up"),
    path('deals/detail/<slug:slug>/', deal_detail, name='deal_detail'),
    path('coupons/', coupons, name="coupons"),
    path('categories/', category_list, name='category_list'),

    # path('login/google/', google_login_view, name='google_login')
]
