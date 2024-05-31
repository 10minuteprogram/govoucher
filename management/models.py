from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.FileField(upload_to='user/profile/images', blank=True, null=True)
    father_name = models.CharField(max_length=150,null=True, blank=True)
    mother_name = models.CharField(max_length=150,null=True, blank=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10,null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200,null=True, blank=True)
    nid = models.IntegerField(null=True, blank=True)
    
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_email_active = models.BooleanField(default=False)
    forget_password_token = models.CharField(max_length=100,blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class Category(models.Model):
    name = models.CharField(max_length=100)
    cover = models.FileField(upload_to="category/images",blank=True, null=True)
    description = models.TextField()
    click_count = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Profile, related_name="crcategories", on_delete=models.SET_NULL, null=True, blank=True)
    upldated_on =  models.DateTimeField(auto_now=True)
    updated_by =  models.ForeignKey(Profile, on_delete=models.SET_NULL,blank=True, null=True, related_name='upcategories')


    def __str__(self):
        return self.name 


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    name = models.CharField(max_length=150)
    cover = models.FileField(upload_to="subcategory/images",blank=True, null=True)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Profile, related_name="crsubcategories", on_delete=models.SET_NULL, null=True, blank=True)
    upldated_on =  models.DateTimeField(auto_now=True)
    updated_by =  models.ForeignKey(Profile, on_delete=models.SET_NULL,blank=True, null=True, related_name='upsubcategories')

    def __str__(self):
        return self.name 

class Brand(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand')
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to="brand/photos",blank=True,null=True)
    cover = models.ImageField(upload_to="brand/covers", blank=True,null=True)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Profile,related_name='crbrands', on_delete=models.SET_NULL,blank=True, null=True)
    upldated_on =  models.DateTimeField(auto_now=True)
    updated_by =  models.ForeignKey(Profile, on_delete=models.SET_NULL,blank=True, null=True, related_name='upbrand')

    def __str__(self):
        return f"{self.name}"
    
class Deal(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,related_name='bdeals',null=True,blank=True)
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to="deal/photos",blank=True,null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    created_by = models.ForeignKey(Profile,related_name='crdeal', on_delete=models.SET_NULL,blank=True, null=True)
    upldated_on =  models.DateTimeField(auto_now=True)
    updated_by =  models.ForeignKey(Profile, on_delete=models.SET_NULL,blank=True, null=True, related_name='updeal')

    def __str__(self):
        return f"{self.name}"


class Coupon(models.Model):
    PERCENTAGE = 'PERCENTAGE'
    FIXED = 'FIXED'
    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage'),
        (FIXED, 'Fixed Amount'),
    ]
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True,blank=True)

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    uses_per_user = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    minimum_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    times_redeemed = models.PositiveIntegerField(default=0)
    last_redeemed = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(User,related_name='crdeals', on_delete=models.SET_NULL, blank=True, null=True)
    updated_by = models.ForeignKey(User,related_name='updeals', on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} | {self.code}"


class Subscribers(models.Model):
    name = models.CharField(max_length=400)
    email = models.EmailField()
    source = models.CharField(max_length=50, blank=True, null=True, default='Manual')
    is_backlist = models.BooleanField(default=False,blank=True, null=True)
    blacklist_reason = models.CharField(max_length=500,blank=True, null=True)
    campaign_sent = models.IntegerField(default=0,blank=True, null=True)
    last_sent = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return f"{self.name} | {self.email}"
    
class EmailCampaign(models.Model):
    CHOICES = [
        ('Subscriber', 'Subscriber'),
        ('User', 'User'),
    ]
    name = models.CharField(max_length=400)
    source = models.CharField(max_length=400, choices=CHOICES)
    total_participant = models.IntegerField()
    body = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=300, blank=True, null=True)


    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name}"

class EmailCampaignParticipant(models.Model):
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.SET_NULL, related_name="campaign", null=True,blank=True)
    subscriber = models.ForeignKey(Subscribers, on_delete=models.SET_NULL, related_name="subscriber", null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL, related_name="user", null=True,blank=True)
    sending_id = models.CharField(max_length=600,blank=True, null=True)
    status = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.campaign} | {self.subscriber if self.subscriber else self.user}"

    
class EmailTemplate(models.Model):
    name = models.CharField(max_length=300)
    subject = models.CharField(max_length=300)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    created_by = models.ForeignKey(Profile, related_name='cremail', on_delete=models.SET_NULL,blank=True, null=True)
    upldated_on =  models.DateTimeField(auto_now=True)
    updated_by =  models.ForeignKey(Profile, on_delete=models.SET_NULL,blank=True, null=True, related_name='upemail')

    def __str__(self):
        return f"{self.name} | {self.subject}"