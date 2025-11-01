

from utils.base_result import BaseResultWithData


class ListCustomerFeedbackQuery:
    @staticmethod
    def query(queryset, request):
        name = request.query_params.get("name")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        feedback = queryset

        if name:
            feedback = feedback.filter(user__icontains=name)

        if start_date:
            feedback = feedback.filter(created_at__date__gte=start_date)

        if end_date:
            feedback = feedback.filter(created_at__date__lte=end_date)

        return BaseResultWithData(
            data=feedback,
            message="Customer feedbacks retrieved successfully",
            status_code=200,
        )