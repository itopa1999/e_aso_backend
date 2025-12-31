from http import HTTPStatus
from apps.aso.models import Product, RecentSearch
from utils.base_result import BaseResultWithData
from utils.log_helpers import OperationLogger


class AddRecentSearchCommand:
    MAX_RECENT_SEARCHES = 15
    
    @staticmethod
    def execute(user, product_id):
        op = OperationLogger(
            "AddRecentSearchCommand",
            user=user.id if user else "Anonymous",
            product_id=product_id
        )
        op.start()
        
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist as e:
            op.fail("Product not found", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.NOT_FOUND,
                message="Product not found"
            )
        
        try:
            # Check if record exists (including soft-deleted ones)
            recent_search = RecentSearch.objects.filter(
                user=user,
                product=product
            ).first()
            
            created = False
            if recent_search is None:
                # Create new record
                recent_search = RecentSearch.objects.create(
                    user=user,
                    product=product
                )
                created = True
            else:
                # If soft-deleted, restore it
                if recent_search.is_deleted:
                    recent_search.is_deleted = False
                    recent_search.save(update_fields=['is_deleted', 'modified_at'])
                else:
                    # Update timestamp if already active
                    recent_search.save(update_fields=['modified_at'])
            
            # If new search and user already has MAX_RECENT_SEARCHES, delete the oldest
            if created:
                search_count = RecentSearch.objects.filter(
                    user=user,
                    is_deleted=False
                ).count()
                
                if search_count > AddRecentSearchCommand.MAX_RECENT_SEARCHES:
                    oldest_search = RecentSearch.objects.filter(
                        user=user,
                        is_deleted=False
                    ).order_by('created_at').first()
                    
                    if oldest_search:
                        oldest_search.delete()
                        op.info(f"Deleted oldest recent search to maintain limit of {AddRecentSearchCommand.MAX_RECENT_SEARCHES}")
            
            op.success("Recent search added successfully")
            return BaseResultWithData(
                data={
                    "id": recent_search.id,
                    "product": product.id,
                    "product_title": product.title,
                    "created_at": recent_search.created_at
                },
                status_code=HTTPStatus.CREATED if created else HTTPStatus.OK,
                message="Recent search added successfully"
            )
        except Exception as e:
            op.fail("Error adding recent search", e)
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Error adding recent search"
            )