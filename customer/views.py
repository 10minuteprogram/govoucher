from django.shortcuts import render
from management.models import *
# Create your views here.
def home(request):
    return render(request, 'customer/home.html')

def deals(request):
    deals = Deal.objects.all()
    deal_view = request.GET.get('deal_view')
    categories = Category.objects.order_by('-click_count')[:10]
 
    context = {
        'deals':deals,
        'categories':categories
    }
    return render(request, 'customer/deals.html',context)
