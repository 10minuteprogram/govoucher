from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import random
from govoucher.postman import send_email
import uuid
from django.http import HttpResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404



# Create your views here.
@login_required(login_url='login')
def home(request):

    return render(request,'management/home.html')

def superuser_list(request):

    superusers = User.objects.filter(is_superuser=True)

    context = {
        "superusers":superusers
    }
    return render(request, 'management/superuser_list.html', context)



def staffs_list(request):
    staff_id = None
    staff = None
     
    staff_users = User.objects.filter(is_staff = True, is_superuser=False)

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        print(staff_id)
        staff = User.objects.get(id=staff_id)
        staff.is_active = not staff.is_active
        staff.save()


        # staff = User.objects.get(id=staff_id)

        # # Toggle the staff status
        # staff.staff_status = not staff.staff_status
        # staff.save()


    context = {
        "staff_users": staff_users,
        "staff_id":staff_id,
        "staff_status":staff
    }


    return render (request, 'management/staffs_list.html', context)

@login_required(login_url='login')
def users(request):

    users = User.objects.filter(is_superuser= False, is_staff = False)

    context = {
        "users" : users
    }

    return render (request, 'management/users.html',context)

def management_profile(request):
    profile = Profile.objects.all()
    context = {
        "profiles": profile
    }

    return render(request, 'accounts/profile.html',context)

def edit_profile(request):

    return render(request, 'accounts/edit_profile.html')


# this is only superuser or staff authentication block.
def login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser or user.is_staff:

                    # geneate random otp
                    if user:
                        otp = random.randint(100000,999999)

                        user.profile.email_verification_code = otp
                        user.profile.save()
                        user.save()
                        print(otp)
                        context = {
                            'otp': otp,
                            'username':username
                        }
                        email = User.objects.get(username=username).email
                        #send_email('Verify your account', [email], 'management/emails/email_verification.html', context, [])
                        return redirect('verify_account')

                    else:
                        messages.error(request, "Invalid username and password")
            else:
                messages.error(request, 'Invalid username and password.')  
        else:
            messages.error(request, "username and password reqired")
 

    return render(request, 'accounts/login.html')

def login_verify(request):

    if request.method == 'POST':
        otp = request.POST.get('otp')

        user_otp = Profile.objects.filter(email_verification_code=otp).first()

        if user_otp:
            user = User.objects.get(id=user_otp.user.id)

            if otp == user_otp.email_verification_code:
                auth_login(request, user)
                #messages.success(request, "Login successful")
                return redirect('home')
            else:
                messages.error(request, "Invalid OTP entered")
        else:
            messages.error(request, "Invalid OTP entered or user not found")




    return render(request, 'accounts/login_verify_email.html')



def logout_view(request):
    logout(request)
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

    return render(request , 'accounts/change-password.html')





def forgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            
            if not User.objects.filter(email=email).first():
                messages.error(request, f'Not email found with this {email}.')
                return redirect('forget-password')
            
            user_obj = User.objects.get(email = email)
            token = str(uuid.uuid4())
            profile_obj= user_obj.user
            profile_obj.forget_password_token = token
            profile_obj.save()
            context = {
                "token" : token,
                "name": profile_obj.user.first_name
            }
            send_email('Change Your Password', [email], 'accounts/change-pass_email.html', context, [])
            messages.success(request, 'Reset your password. Please check your email inbox.')
            return redirect('forget-password')
                
    
    
    except Exception as e:
        print(e)
    return render(request , 'accounts/forget-password.html')


def create_staff(request):
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        father_name = request.POST.get('father_name')
        mother_name = request.POST.get('mother_name')
        phone = request.POST.get('phone')
        nid = request.POST.get('nid')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        birth_date = request.POST.get('birth_date')

        is_staff = True
        password = str(random.randint(10000000,99999999))

        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")

        #create staff account
        user = User.objects.create_user(
            username=username,
            first_name = first_name,
            last_name = last_name,
            email=email,
            password=password,
            is_staff=is_staff
        )
        profile = user.profile
        
        # Update the existing profile if necessary
        profile.father_name = father_name
        profile.mother_name = mother_name
        profile.phone = phone
        profile.nid = nid
        profile.address = address
        profile.gender = gender
        profile.birth_date = birth_date
        profile.save()

        context = {
            'username': username,
            'first_name':first_name,
            'password': password,
        }        
        print(password)
        send_email('your staff account', [email], 'management/emails/staff_info_email.html', context, [])

        #messages.success(request, 'Staff user created successfully.')
        return redirect('staffs_list')
    
    return render(request, 'management/create_staff.html')

def create_superuser(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        # password = request.POST.get('password')
        # password2 = request.POST.get('password2')


        if  not all([first_name, username, email]):
            messages.error(request,'Please fill out the required fields!')
            return redirect('create_superuser')

        try:
            u = User.objects.get(username=username)
            messages.error(request,"Username already exists.")
            return redirect('create_superuser')
        except ObjectDoesNotExist:
            pass
        # if len(password) < 8:
        #     messages.error(request,'Password must be at least 8 characters long.')
        #     return redirect('create_superuser')
        # elif password != password2:
        #     messages.error(request,'Passwords do not match. Please enter both passwords correctly.')
        #     return redirect('create_superuser')
        password = str(random.randint(10000000,99999999))
        print(password)
        user = User.objects.create_superuser(
            username=username,  
            first_name=first_name,  
            last_name=last_name,   
            email=email)
        user.set_password(password)
        user.save()

        context  = {
            "username":username,
            "first_name":first_name,
            "password":password,
        }
        send_email('your superuser account', [email], 'management/emails/s_admin_info_email.html', context, [])
        #messages.success(request, "Superuser account has been created successfully.")
        return redirect('superuser_list')



    return render(request,'management/create_superuser.html')

def add_category(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')

        if name and image and description:
            Category.objects.create(
                name=name,
                cover=image,
                description=description,
                created_by= Profile.objects.get(user=request.user)
            )
            return redirect('category')
        else:
            messages.error(request,"All fields are required")

    return render(request, 'management/add_category.html')


def category(request):

    categorys =  Category.objects.all()

    if request.method=='POST':
        delete_item = request.POST.get("delete_item")
        if delete_item:
            item = get_object_or_404(Category, id=delete_item)
            item.delete()
            #messages.success(request, f"{item} is deleted Successfully")
            return redirect('category')

    context = {
        'categorys': categorys,
    }

    return render(request, 'management/category.html',context)

def add_subCategory(request):
    category_id = None
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = int(request.POST.get('category_id'))
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')

        if name and description and category_id:
            SubCategory.objects.create(
               category_id=category_id,
               name=name,
               cover=image,
               description=description,
               created_by=Profile.objects.get(user=request.user),
            )
            return redirect('subCategory')
        else:
            messages.error(request,'Please enter all the details')


    context = {
        "categories": categories,
    }

    return render(request, 'management/add_subCategory.html',context)


def subCategory(request):
    subcategors = None

    categorys = Category.objects.all()


    if request.method == 'GET':
        search = request.GET.get("name")
        if search:
            # Filter subcategories based on search query
            subcategors = SubCategory.objects.filter(category_id=search)
        else:
            subcategors = SubCategory.objects.all()
                

    context = {
        'subcategors' : subcategors,
        'categorys' : categorys,
    }
    
    return render(request,  'management/subCategory.html',context)

def add_brand(request):
    category_id = None
    sub_categorys = None
    sub_category_id = None
    categories = Category.objects.all()

    if request.method == 'POST':
        try:
            category_id = int(request.POST.get("category_id"))
        except:
            category_id = None

        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')

        sub_category_id = request.POST.get('sub_category_id')

        if not sub_category_id:
            sub_categorys = SubCategory.objects.filter(category_id=category_id)
        elif sub_category_id and name:
            Brand.objects.create(
                sub_category_id = sub_category_id,
                name = name,
                photo = image,
                description = description,
                created_by = Profile.objects.get(user=request.user),
            )
            return redirect('brand_list')

    context  ={
        'categories' : categories,
        'sub_categorys' : sub_categorys,
        # 'sub_category_id':sub_category_id
    }



    return render(request,"management/add_brand.html",context)

def brand_list(request):


    brands = SubCategory.objects.all()

    if request.method == 'GET':
        search = request.GET.get("name")
        if search:
            # Filter subcategories based on search query
            all_brand = Brand.objects.filter(sub_category_id=search)
        else:
            all_brand = Brand.objects.all()

    context ={
        'brands' : all_brand,
        'brand':brands,
    }

    return render(request,"management/brand_list.html",context)

def deal_list(request):

    all_brand = None
    deals = None

    deals = Brand.objects.all()

    if request.method == 'GET':
        search = request.GET.get("name")
        if search:
            # Filter subcategories based on search query
            all_brand = Deal.objects.filter(brand_id=search)
        else:
            all_brand = Deal.objects.all()

    context ={
        "deals" : deals,
        "all_brand":all_brand,
    }
    return render(request, 'management/deal-list.html',context)

def add_deal(request):
    categories = Category.objects.all()
    sub_categorys = None
    brands = None

    category_id = None
    sub_category_id = None


    if request.method == "POST":
        try:
            category_id = int(request.POST.get("category_id"))
        except:
            category_id = None


        try:
            sub_category_id = int(request.POST.get('sub_category_id'))
        except:
            sub_category_id = None
        
        name = request.POST.get("name")
        brand_id = request.POST.get('brand_id')
        
        if category_id:
            sub_categorys = SubCategory.objects.filter(category_id=category_id)
        
        if sub_category_id:
            brands = Deal.objects.filter(sub_category_id=sub_category_id)
            print(brands)
        

        
        if sub_category_id and name:
            Deal.objects.create(
                name = name,
                sub_category_id = sub_category_id,
                brand_id = brand_id,
            )
            return redirect('deal_list')


    context ={
        'categories': categories,
        'sub_categorys': sub_categorys,
        'brands': brands,

        'category_id' : category_id,
        'sub_category_id':sub_category_id,
    }

    return render(request, 'management/add_deal.html',context)
