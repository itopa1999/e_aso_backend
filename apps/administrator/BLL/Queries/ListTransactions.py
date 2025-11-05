

from utils.base_result import BaseResultWithData


class TransactionListQuery:
    @staticmethod
    def query(request, queryset):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        elif end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        return BaseResultWithData(
            data=queryset,
            status_code=200,
            message="Transactions fetched successfully."
        )