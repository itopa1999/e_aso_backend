from django.db.models import Q

from apps.administrator.serializers import ContactFormSubmissionSerializer
from utils.base_result import BaseResultWithData

class ContactFormSubmissionListQuery:
    @staticmethod
    def query(request, base_qs):
        search_query = request.query_params.get('search', None)
        if search_query:
            base_qs = base_qs.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(message__icontains=search_query)
            )

        ordering = request.query_params.get('ordering', '-created_at')
        base_qs = base_qs.order_by(ordering)
        
        serializer = ContactFormSubmissionSerializer(base_qs, many=True)
        base_qs = serializer.data
        
        return BaseResultWithData(
            status_code=200,
            message="Contact form submissions retrieved successfully.",
            data=base_qs
        )