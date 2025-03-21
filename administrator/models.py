from datetime import timedelta
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from administrator.manager import UserManager

# Create your models here.


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=40, unique=True)
    state_code = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_picture/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.profile_picture:
            import os
            import random
            from django.conf import settings
            
            # List all files in the 'profile_picture' folder
            profile_pictures_path = os.path.join(settings.MEDIA_ROOT, 'profile_picture')
            profile_pictures = os.listdir(profile_pictures_path)

            # Pick a random profile picture
            random_picture = random.choice(profile_pictures)

            # Set the profile picture path
            self.profile_picture = f"profile_picture/{random_picture}"
        super().save(*args, **kwargs)

    objects=UserManager( )
    USERNAME_FIELD ='email'
    REQUIRED_FIELDS=[]

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id']),
        ]
    
    def __str__(self):
        return f"{self.email}"
    
    

class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_token(self):
        """Generate a 6-digit token"""
        self.token = str(random.randint(100000, 999999))
        self.created_at = timezone.now()

    def is_token_expired(self):
        """Check if token is expired (valid for 10 minutes)"""
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"Verification for {self.user.email}"
    
    