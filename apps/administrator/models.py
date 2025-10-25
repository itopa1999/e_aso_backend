from django.db import models

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