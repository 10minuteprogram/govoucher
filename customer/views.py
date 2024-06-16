from django.shortcuts import render
from management.models import *
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
    return render(request, 'customer/coupon.html')


def sign_in(request):
    return render(request, 'customer/sign_in.html')

def sign_up(request):
    return render(request, 'customer/sign_up.html')



def category_list(request):
    categories = Category.objects.all()
    return render(request, 'customer/test.html', {'categories': categories})
# def google_login_view(request):
#     # Redirect the user to the Google authentication URL provided by django-allauth
#     return redirect('/accounts/google/login/')