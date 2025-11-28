from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from utils.base_model import BaseModel
from utils.enum import BannerCategoryNames

# Create your models here.

class Banner(BaseModel):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True, null=True, choices=BannerCategoryNames.choices())
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["link"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return self.title
    

class CustomerFeedback(BaseModel):
    user = models.CharField(max_length=100)
    feedback = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, "Rating must be at least 1 star"),
            MaxValueValidator(5, "Rating cannot be greater than 5 stars")
        ]
    )
    is_done = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Feedback from {self.user} - Rating: {self.rating}"
    
    def clean(self):
        """Additional validation at model level"""
        from django.core.exceptions import ValidationError
        if self.rating < 1 or self.rating > 5:
            raise ValidationError({'rating': 'Rating must be between 1 and 5 stars.'})