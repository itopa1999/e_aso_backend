from apps.aso.models import Product
from utils.base_result import BaseResultWithData
from django.db import transaction
from utils.log_helpers import OperationLogger


class BulkUpdateProductBadgesCommand:
    @staticmethod
    def execute(view, request):
        op = OperationLogger(
            "BulkUpdateProductBadgesCommand",
            user=request.user.id if request.user and request.user.is_authenticated else "Anonymous"
        )
        op.start()
        
        serializer = view.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        badge = validated_data['badge']
        product_ids = validated_data.get('product_ids', [])
        product_titles = validated_data.get('product_titles', [])
        
        with transaction.atomic():
            updated_count = 0

            # Update by IDs
            if product_ids:
                count_by_id = Product.objects.filter(
                    id__in=product_ids, is_deleted=False
                ).update(badge=badge)
                updated_count += count_by_id

            # Update by titles
            if product_titles:
                count_by_title = Product.objects.filter(
                    title__in=product_titles, is_deleted=False
                ).update(badge=badge)
                updated_count += count_by_title

            op.success(f"Updated {updated_count} product badges")
            return BaseResultWithData(
                data={'updated_count': updated_count},
                message="Product badges updated successfully",
                status_code=200
            )