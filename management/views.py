from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import random
from govoucher.postman import send_email
import uuid
from .helpers import send_forget_password_mail

# Create your views here.
def home(request):

    return render(request,'management/home.html')

def superuser_list(request):

    superusers = User.objects.filter(is_superuser=True)

    context = {
        "superusers":superusers
    }
    return render(request, 'management/superuser_list.html', context)



def staffs_list(request):
     
    staff_users = User.objects.filter(is_staff = True, is_active=True, is_superuser=False)

    context = {
        "staff_users": staff_users
    }


    return render (request, 'management/staffs_list.html', context)


def users(request):

    users = User.objects.filter(is_superuser= False, is_staff = False)

    context = {
        "users" : users
    }

    return render (request, 'management/users.html',context)



# this is authentication block.
def login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        passwoed = request.POST.get('password')

        if username and passwoed:
            user = authenticate(request, username=username, password=passwoed)

            if user:
                auth_login(request,user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username and password")
        else:
            messages.error(request, "username and password reqired")
    


    return render(request, 'accounts/login.html')

def login_view(request):
    logout(request,)
    return redirect('login')


def sign_up(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and email and password:
            # check if the username alredey exists
            has_already = User.objects.filter(username=username).first()
            if has_already:
                messages.error(request,f"Username {username} already exists! Please try another one.")
                return redirect(sign_up)
            
            # check if the email alredey exists
            has_already = User.objects.filter(email=email).first()
            if has_already:
                messages.error(request,f"email {email} already exists! Please try another one.")
                return redirect(sign_up)
            
            # create a new user
            user = User.objects.create_user(username, email, password)

            # geneate random otp
            otp = random.randint(100000,999999)

            user.profile.email_verification_code = otp
            user.profile.save()
            user.save()
            context = {
                'otp': otp,
                'username': username,
            }
            send_email('Verify your Sports account', [email], 'management/emails/email_verification.html', context, [])
            


            messages.success(request, 'Sing_up successfully')
            return redirect('login')
        else:
            messages.error(request,"All fields are required")
            return redirect('sign_up')


    return render(request, 'accounts/sign_up.html')



def changePassword(request , token):
    context = {}
    
    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}
        
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change-password/{token}/')
                
            
            if  new_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect(f'/change-password/{token}/')
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('login')
            
            
    except Exception as e:
        print(e)
    return render(request , 'accounts/change-password.html' , context)





def forgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            
            if not User.objects.filter(email=email).first():
                messages.success(request, f'Not email found with this {email}.')
                return redirect('forget-password')
            
            user_obj = User.objects.get(email = email)
            token = str(uuid.uuid4())
            profile_obj= Profile.objects.get(user = user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_mail(user_obj.email , token)
            messages.success(request, 'Reset your password. Please check your email inbox.')
            return redirect('forget-password')
                
    
    
    except Exception as e:
        print(e)
    return render(request , 'accounts/forget-password.html')


def create_staff(request):
    
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = True

        #create staff account
        user = User.objects.create_user(username=username, email=email, password=password, is_staff=is_staff)

        messages.success(request, 'Staff user created successfully.')
        return redirect('staffs_list')


    return render(request, 'management/create_staff.html')

#hhhhhhhhh