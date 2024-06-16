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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from .email_send import send_email_from_db




# Create your views here.
@login_required(login_url='login')
def home(request):

    return render(request,'management/home.html')

def superuser_list(request):

    superusers = User.objects.filter(is_superuser=True)
    paginator = Paginator(superusers, 10) # Show 12 users per page.

    page = request.GET.get('page', 1)

    try:
        superusers = paginator.page(page)
    except PageNotAnInteger:
        superusers = paginator.page(1)
    except EmptyPage:
        superusers = paginator.page(paginator.num_pages)

    context = {
        "superusers":superusers
    }
    return render(request, 'management/superuser_list.html', context)

def superuser_profile(request, id):
    super_profiles = User.objects.filter(id=id).first()
    
    context={
        "super_profile":super_profiles
    }
    return render(request, 'accounts/superuser_profile.html',context)

def staffs_list(request):

    staff = None
     
    staff_users = User.objects.filter(is_staff = True, is_superuser=False)
    paginator = Paginator(staff_users, 4) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        staff_users = paginator.page(page)
    except PageNotAnInteger:
        staff_users = paginator.page(1)
    except EmptyPage:
        staff_users = paginator.page(paginator.num_pages)



    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        print(staff_id)
        if staff_id:
            try:
                staff = User.objects.get(id=staff_id)
                staff.is_active = not staff.is_active
                staff.save()
            except User.DoesNotExist:
                return HttpResponse("Invalid staff ID provided.")
        else:
            return HttpResponse("No staff ID provided.")

    # if request.method == 'POST':
    #     reset_pass = request.POST.get('reset_pass')
    #     staff_pass = User.objects.filter(id=reset_pass).first()
    #     email = staff_pass.email
    #     print(staff_pass, email)
    #     #send_email('Verify your account', [email], 'management/emails/email_verification.html', context, [])



    context = {
        "staff_users": staff_users,
        "staff_status":staff
    }


    return render (request, 'management/staffs_list.html', context)

@login_required(login_url='login')
def users(request):
    user_id = None
    users = User.objects.filter(is_superuser= False, is_staff = False)
    email_campaigns = EmailCampaign.objects.all()
    templates = EmailTemplate.objects.all()

    q = request.GET.get('q')
    if q:
        users = users.filter(email__icontains=q)
    
    if request.method == 'POST':
        # participant filter criteria
        q = request.POST.get('q')
        if q:
            users = users.filter(email__icontains=q)
            
        name = request.POST.get('name')
        template_id = request.POST.get('template_id')
        template = EmailTemplate.objects.filter(id=template_id).first()
        if not template:
            messages.error(request, 'Template not found')
            return redirect('users')

        body = template.body
        subject = template.subject
        total_participant = users.count()
        source = 'User'


        campaign = EmailCampaign.objects.create(
            name=name,
            source=source,
            total_participant=total_participant,
            body=body,
            subject=subject,
            created_by=request.user
        )
        for u in users:
            EmailCampaignParticipant.objects.create(
                campaign=campaign,
                user=u,
                status='Created'
            )
        
        messages.success(request, 'Campaign has been created successfully!')
        return redirect('email_campaign')

    paginator = Paginator(users, 10) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(user_id)
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()

    context = {
        "users" : users,
        "user_id":user_id,
        "email_campaigns":email_campaigns,
        "templates":templates,

    }

    return render (request, 'management/users.html',context)

def management_profile(request):
    profiles = Profile.objects.all()

    user = request.user
    profile = user.profile

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email') 
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        birth_date = request.POST.get('birth_date')


        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            pass
            print("Invalid date format")

        if  full_name and email and phone and address and birth_date:
            # Update profile fields with form data
            user.first_name = full_name
            user.email = email
            profile.phone = phone
            profile.address = address
            profile.birth_date = birth_date

            # Save changes to both user and profile
            user.save()
            profile.save()
        else:
            messages.error(request,"Please fill out all the required fields.")




    context = {
        "profiles": profiles,
    }

    return render(request, 'accounts/profile.html',context)

def staff_profile(request, id):
    staff_profiles = User.objects.filter(id=id).first()
    
    context={
        "staff_profiles":staff_profiles
    }

    return render(request, 'accounts/staff_profile.html',context)
    


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
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # or the appropriate backend
                auth_login(request, user)
                #messages.success(request, "Login successful")

                # Check if the user is a superuser or staff
                if user.is_superuser:
                    return redirect('home')  # URL name for admin dashboard
                elif user.is_staff:
                    return redirect('home')
                
            else:
                messages.error(request, "Invalid OTP entered")
        else:
            messages.error(request, "Invalid OTP entered or user not found")




    return render(request, 'accounts/login_verify_email.html')


def resend_otp(request):
    # Assuming the user is authenticated and their profile is accessible via request.user.profile
    profile = Profile.objects.get(user=request.user)
    
    # Generate a new OTP (You can use a better OTP generation mechanism)
    new_otp = random.randint(100000, 999999)
    print(new_otp)
    
    # Update the OTP in the user's profile
    profile.email_verification_code = new_otp
    profile.save()
    
    # Send the new OTP to the user's email
    # (You should implement the send_email function)
    # send_email(profile.user.email, "Your new OTP", f"Your new OTP is {new_otp}")
    
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_account')



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
        #send_email('your staff account', [email], 'management/emails/staff_info_email.html', context, [])

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

    #update category or delete category
    if request.method == 'POST':
        delete_item = request.POST.get("delete_item")
        if delete_item:
            item = categorys.get(id=delete_item)
            item.delete()
            #messages.success(request, f"{item} is deleted Successfully")
            return redirect('category')
        else:
            pass
        
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')

        if category_id and name and image and description:
            category = categorys.get(id=category_id)
            category.name = name
            category.cover = image
            category.description = description
            category.save()
            messages.success(request, f"{category} is updated Successfully")
            return redirect('category')
        else:
            messages.error(request,"All fields are required")

    # pagination
    paginator = Paginator(categorys, 5) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        categorys = paginator.page(page)
    except PageNotAnInteger:
        categorys = paginator.page(1)
    except EmptyPage:
        categorys = paginator.page(paginator.num_pages)


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

    #update sub-category
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        if subcategory_id:
            subcategor = SubCategory.objects.get(id=subcategory_id)
            subcategor.category_id = category_id
            subcategor.name = name
            subcategor.cover = image
            subcategor.description = description
            subcategor.save()

            return redirect('subCategory')
        
    #delete category
    if request.method=='POST':
        delete_item = request.POST.get("delete_item")
        print(delete_item)
        # if delete_item:
        #     item = get_object_or_404(Category, id=delete_item)
        #     item.delete()
        #     #messages.success(request, f"{item} is deleted Successfully")
        #     return redirect('category')

    if request.method == 'GET':
        search = request.GET.get("name")
        if search:
            # Filter subcategories based on search query
            subcategors = SubCategory.objects.filter(category_id=search)
        else:
            subcategors = SubCategory.objects.all()

    # pagination
    paginator = Paginator(subcategors, 5) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        subcategors = paginator.page(page)
    except PageNotAnInteger:
        subcategors = paginator.page(1)
    except EmptyPage:
        subcategors = paginator.page(paginator.num_pages)

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
    all_brand = None
    sub_categorys = SubCategory.objects.all()

    #update_brand
    if request.method == 'POST':
        subcategory_id = request.POST.get('subcategory_id')
        brand_id = request.POST.get('brand_id')
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        print(subcategory_id,brand_id,name,image,description)
        if brand_id:
            brand = Brand.objects.get(id=brand_id)
            brand.sub_category_id = subcategory_id
            brand.name = name
            brand.cover = image
            brand.description = description
            brand.save()

            return redirect('brand_list')


    if request.method == 'GET':
        search = request.GET.get("name")
        if search:
            # Filter subcategories based on search query
            all_brand = Brand.objects.filter(sub_category_id=search)
        else:
            all_brand = Brand.objects.all()

        # pagination
        paginator = Paginator(all_brand, 5) # pagination Show 10 users per page.

        page = request.GET.get('page', 1)

        try:
            all_brand = paginator.page(page)
        except PageNotAnInteger:
            all_brand = paginator.page(1)
        except EmptyPage:
            all_brand = paginator.page(paginator.num_pages)

    context ={
        'brands' : all_brand,
        'sub_categorys':sub_categorys,
    }

    return render(request,"management/brand_list.html",context)

def deal_list(request):

    all_brand = None
    deals = None

    all_brand = Brand.objects.all()

    #update_brand
    if request.method == 'POST':
        brand_id = request.POST.get('brand_id')
        deal_id = request.POST.get('deal_id')
        name = request.POST.get('name')
        if deal_id:
            deal = Deal.objects.get(id=deal_id)
            deal.brand_id = brand_id
            deal.name = name
            deal.save()
            return redirect('deal_list')

    if request.method == 'GET':
        search = request.GET.get("name")
        if search:
            # Filter subcategories based on search query
            deals = Deal.objects.filter(brand_id=search)
        else:
            deals = Deal.objects.all()

        # pagination
        paginator = Paginator(deals, 5) # pagination Show 10 users per page.

        page = request.GET.get('page', 1)

        try:
            deals = paginator.page(page)
        except PageNotAnInteger:
            deals = paginator.page(1)
        except EmptyPage:
            deals = paginator.page(paginator.num_pages)

    context ={
        "all_brand" : all_brand,
        "deals":deals,
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
            brands = Brand.objects.filter(sub_category_id=sub_category_id)
            print(brands)
        

        
        if sub_category_id and name:
            Deal.objects.create(
                name = name,
                brand_id = brand_id,
                created_by = Profile.objects.get(user=request.user),
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

def coupon(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons': coupons,
        }
    return render(request, 'management/coupon.html',context)


def subscriber(request):
    subscribers = Subscribers.objects.all()
    email_campaigns = EmailCampaign.objects.all()
    templates = EmailTemplate.objects.all()

    email = request.GET.get('email')
    campaign_sent = request.GET.get('campaign_sent')
    last_sent = request.GET.get('last_sent')

    # Apply additional filters based on parameters
    if email:
        subscribers = subscribers.filter(email__icontains=email)
    if campaign_sent:
        subscribers = subscribers.exclude(campaign_sent=campaign_sent)
    if last_sent:
        subscribers = subscribers.exclude(last_sent__date=last_sent)


    # pagination
    paginator = Paginator(subscribers, 10) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        subscribers = paginator.page(page)
    except PageNotAnInteger:
        subscribers = paginator.page(1)
    except EmptyPage:
        subscribers = paginator.page(paginator.num_pages)

    context = {
        'subscribers': subscribers,
        'email_campaigns': email_campaigns,
        'templates': templates,
    }
    return render(request, 'management/subscriber.html',context)


def create_campaign(request):
    if request.method == 'POST':
        # participant filter criteria
        participants = Subscribers.objects.all()
        q = request.POST.get('q')
        if q:
            participants = participants.filter(email__icontains=q)

        name = request.POST.get('name')
        template_id = request.POST.get('template_id')
        template = EmailTemplate.objects.filter(id=template_id).first()
        if not template:
            messages.error(request, 'Template not found')
            return redirect('subscriber')

        body = template.body
        subject = template.subject
        total_participant = participants.count()
        source = request.GET.get('source')


        campaign = EmailCampaign.objects.create(
            name=name,
            source=source,
            total_participant=total_participant,
            body=body,
            subject=subject,
            created_by=request.user
        )

        for participant in participants:
            EmailCampaignParticipant.objects.create(
                campaign=campaign,
                subscriber=participant,
                status='Created'
            )
        
        messages.success(request, 'Campaign has been created successfully!')
        return redirect('subscriber')

    return redirect('subscriber')

def email_campaign(request):
    email_campaigns = EmailCampaign.objects.all()

    #filter
    name = request.GET.get('name')
    source = request.GET.get('source')
    total_participants = request.GET.get('total_participants')

    if name:
        email_campaigns = email_campaigns.filter(name__icontains=name)
    if source:
        email_campaigns = email_campaigns.filter(source__icontains=source)
    if total_participants:
        email_campaigns = email_campaigns.filter(total_participant=total_participants)

    # pagination
    paginator = Paginator(email_campaigns, 5) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        email_campaigns = paginator.page(page)
    except PageNotAnInteger:
        email_campaigns = paginator.page(1)
    except EmptyPage:
        email_campaigns = paginator.page(paginator.num_pages)


    context = {
        'email_campaigns': email_campaigns,
    }
    return render(request, 'management/email_campaign.html', context)

def campaign_details(request, id):
    campaign = EmailCampaign.objects.get(id=id)
    participants = EmailCampaignParticipant.objects.filter(campaign=campaign)

    context = {
        'campaign': campaign,
        'participants': participants,
    }
    return render(request, 'management/campaign_details.html',context)

def send_email(request):
    if request.method == "POST":
        campaign_id = request.POST.get("campaign_id")
        campaign = EmailCampaign.objects.get(id=campaign_id)
        participants = EmailCampaignParticipant.objects.filter(campaign=campaign)

        try:
            email_template = campaign.body
            email_subject = campaign.subject
        except EmailTemplate.DoesNotExist:
            return
        
        # Send email to all participants
        for participant in participants:
            email = participant.subscriber.email if participant.subscriber else participant.user.email
            # Send email
            send_email_from_db(email_subject, [email], email_template)

            # Update campaign_sent field
            email_campaigns = Subscribers.objects.filter(email=email)
            for email_campaign in email_campaigns:
                email_campaign.campaign_sent += 1
                email_campaign.last_sent = timezone.now()  # Update last_sent to current time
                email_campaign.save()

        messages.success(request,"Email sent successfully to all participants!")
        return redirect(reverse('campaign_details', kwargs={'id': campaign_id}))
    else:
        return HttpResponse("Method not allowed.")

def email_template(request):
    email_templates = EmailTemplate.objects.all()

    if request.method == 'POST':
        template_id = request.POST.get('template_id')  # Assuming you have a hidden input field for template ID in your form
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        if template_id and name and subject and body:
            email_template = email_templates.get(id=template_id)
            email_template.name = name
            email_template.subject = subject
            email_template.body = body
            email_template.save()
            messages.success(request, 'Campaign has been updated successfully!')
            return redirect('email_template')
        
    # pagination
    paginator = Paginator(email_templates, 5) # pagination Show 10 users per page.

    page = request.GET.get('page', 1)

    try:
        email_templates = paginator.page(page)
    except PageNotAnInteger:
        email_templates = paginator.page(1)
    except EmptyPage:
        email_templates = paginator.page(paginator.num_pages)
    context = {
        'email_templates': email_templates,
    }

    return render(request, 'management/email_template.html',context)

def add_email_template(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        if name and subject and body :
            EmailTemplate.objects.create(
                name=name,
                subject=subject,
                body=body,
                created_by = Profile.objects.get(user=request.user),
            )
            return redirect('email_template')

    return render(request, 'management/add_email_template.html')