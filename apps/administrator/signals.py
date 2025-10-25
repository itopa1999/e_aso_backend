from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from apps.administrator.models import Banner
from utils.Middlewares.threadlocals import get_current_user
from utils.base_model import BaseModel
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

@receiver(pre_save)
def auto_fill_audit_fields(sender, instance, **kwargs):
    # Only for models inheriting from BaseModel
    if not issubclass(sender, BaseModel):
        return

    user = get_current_user()
    action_by = getattr(user, "first_name", None) or getattr(user, "email", None) or "System"

    if instance._state.adding:
        if not instance.created_by:
            instance.created_by = action_by
    else:
        instance.modified_by = action_by

    if instance.is_deleted and not instance.deleted_at:
        instance.deleted_at = timezone.now()
        instance.deleted_by = action_by
        
        

@receiver([post_save, post_delete], sender=Banner)
def banner_model_changed(sender, instance, **kwargs):
    GlobalCache.delete_prefix("banner_")