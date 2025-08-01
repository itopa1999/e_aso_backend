from datetime import timedelta
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator


from administrator.manager import UserManager

# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=40, unique=True)
    phone_regex = RegexValidator(
        regex=r'^(?:\+234|0)[789][01]\d{8}$',
        message="Phone number must be a valid Nigerian number (e.g., 08012345678 or +2348012345678)."
    ) 
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        super().save(*args, **kwargs)

    objects=UserManager( )
    USERNAME_FIELD ='email'
    REQUIRED_FIELDS=['first_name',"last_name"]

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
    
    