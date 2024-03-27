from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.FileField(upload_to='user/profile/images', blank=True, null=True)
    father_name = models.CharField(max_length=150,null=True, blank=True)
    mother_name = models.CharField(max_length=150,null=True, blank=True)
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
    sub_category = models.ForeignKey(SubCategory,on_delete=models.SET_NULL,related_name='deals', blank=True, null=True)
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,related_name='bdeals',null=True,blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"