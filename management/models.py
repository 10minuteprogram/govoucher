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
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



