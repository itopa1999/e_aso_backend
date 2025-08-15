from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User

@receiver(m2m_changed, sender=User.groups.through)
def assign_rider_number(sender, instance, action, reverse, pk_set, **kwargs):
    if action == "post_add" and not reverse:
        # Get the "Rider" group
        try:
            rider_group = Group.objects.get(name__iexact="rider")
        except Group.DoesNotExist:
            return
        
        # Check if Rider group was just added
        if rider_group.id in pk_set and not instance.rider_number:
            # Count only users in the Rider group with a rider_number
            last_rider = (
                User.objects.filter(groups=rider_group)
                .exclude(rider_number__isnull=True)
                .exclude(rider_number="")
                .order_by("-id")
                .first()
            )

            if last_rider and last_rider.rider_number:
                # Extract last number
                try:
                    last_number = int(last_rider.rider_number.split("-")[-1])
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1

            # Format: A0-DR-xxxx
            instance.rider_number = f"A0-DR-{str(new_number).zfill(4)}"
            instance.save()
