from datetime import timedelta
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator

from apps.users.manager import UserManager
from utils.base_model import BaseModel

# Create your models here.

import string, random

from utils.enum import FeatureNames, TransactionChannel, TransactionStatus, TransactionType

def generate_referral_code(length=10):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not User.objects.filter(referral_code=code).exists():
            return code


class User(BaseModel, AbstractUser):
    username = None
    email = models.EmailField(max_length=40, unique=True)
    phone_regex = RegexValidator(
        regex=r'^(?:\+234|0)[789][01]\d{8}$',
        message="Phone number must be a valid Nigerian number (e.g., 08012345678 or +2348012345678)."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        blank=True,
        null=True
    )
    rider_number = models.CharField(max_length=40, unique=True, null=True, blank=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, editable=False, null=True)
    is_referral_qualified = models.BooleanField(default=False)
    referral_used = models.BooleanField(default=False)
    referral_used_purchase = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        
        if not self.referral_code:
            self.referral_code = generate_referral_code(10).upper()
            
        super().save(*args, **kwargs)
        
    @property
    def check_referral_qualification(self):
        from utils.feature_flags import is_feature_enabled

        flag, enable = is_feature_enabled(FeatureNames.REFERRAL_SYSTEM.value)
        if not enable:
            return False

        successful_referrals = self.referrals_made.filter(successful=True).count()
        qualified = successful_referrals >= 5

        if self.is_referral_qualified != qualified:
            self.is_referral_qualified = qualified
            self.save(update_fields=["is_referral_qualified"])

        return qualified
    

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
    
    

class UserVerification(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
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
    
    

class Referral(BaseModel):
    referrer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="referrals_made"
    )
    referee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="referrals_received"
    )
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("referrer", "referee")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.referrer.first_name} → {self.referee.first_name} ({'✅' if self.successful else '❌'})"
    
    
class Transaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=TransactionType.choices())
    reference = models.CharField(max_length=100, unique=True)
    channel = models.CharField(max_length=50, choices=TransactionChannel.choices())
    status = models.CharField(max_length=20, choices=TransactionStatus.choices())
    order_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount}"