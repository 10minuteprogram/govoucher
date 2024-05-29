from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'customer/home.html')

def deals(request):
    return render(request, 'customer/deals.html')
