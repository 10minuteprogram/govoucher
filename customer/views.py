from django.shortcuts import render
from management.models import *
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login, logout
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
import uuid
from govoucher.postman import send_email


# Create your views here.
def home(request):
    return render(request, 'customer/home.html')

def deals(request):
    subcategories = SubCategory.objects.all()

    deals = Deal.objects.all()
    categories = Category.objects.order_by('-click_count')[:10]
 
    # Check if the request is for subcategories
    category_id = request.GET.get('id')
    if category_id:
        subcategories = subcategories.filter(category_id=category_id)


    #deal_view drid and list
    deal_view = request.GET.get('deal_view', 'grid')

    page = request.GET.get('page', 1)

    paginator = Paginator(deals, 8)
    try:
        deals = paginator.page(page)
    except PageNotAnInteger:
        deals = paginator.page(1)
    except EmptyPage:
        deals = paginator.page(paginator.num_pages)

    context = {
        'deals':deals,
        'categories':categories,
        'deal_view':deal_view,
        'subcategories':subcategories,
        
    }
    return render(request, 'customer/deals.html',context)

def deal_detail(request, slug):
    deal = Deal.objects.get(slug=slug)

    context = {
        'deal':deal
        }
    
    return render(request, 'customer/deal-detail.html',context)


def coupons(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons':coupons
    }
    return render(request, 'customer/coupon.html', context)


def sign_in(request):
    return render(request, 'customer/sign_in.html')

def sign_up(request):
    return render(request, 'customer/sign_up.html')

def customer_profile(request):
    try:
        google_account = request.user.socialaccount_set.get(provider='google')
        logged_in_with_google = True
    except SocialAccount.DoesNotExist:
        logged_in_with_google = False

    context = {
        'profile':request.user.profile,
        'logged_in_with_google':logged_in_with_google
    }
    return render(request, 'customer/profile.html',context)

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'customer/test.html', {'categories': categories})
# def google_login_view(request):
#     # Redirect the user to the Google authentication URL provided by django-allauth
#     return redirect('/accounts/google/login/')

def logout_view(request):
    logout(request)
    return redirect('home')

def forget_Password(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            
            if not User.objects.filter(email=email).first():
                messages.error(request, f'Not email found with this {email}.')
                return redirect('forget_Password')
            
            user_obj = User.objects.get(email = email)
            token = str(uuid.uuid4())
            profile_obj= user_obj.user
            profile_obj.forget_password_token = token
            profile_obj.save()
            context = {
                "token" : token,
                "name": profile_obj.user.first_name
            }
            # send_email('Change Your Password', [email], 'accounts/change-pass_email.html', context, [])
            # messages.success(request, 'Reset your password. Please check your email inbox.')
            return redirect('forget_Password')
                
    
    
    except Exception as e:
        print(e)
    return render(request , 'customer/forget_password.html')

def change_password(request , token):

    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        if not profile_obj:
            return HttpResponse("Invalid Token")
        
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')
            user_id = profile_obj.user.id
            if new_password and confirm_password and user_id:       
                
                if  new_password != confirm_password:
                    messages.error(request, 'both should  be equal.')
                    return redirect(f'change-password{token}')
                
                user_obj = profile_obj.user
                user_obj.set_password(new_password)
                user_obj.save()
                return redirect('login')
            else:
                messages.error(request,"Please enter your new password.")
            
    except Exception as e:
        print(e)

    return render(request , 'customer/change_password.html')