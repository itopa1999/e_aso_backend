

from http import HTTPStatus
from apps.administrator.serializers import ProductImportSerializer
from utils.base_result import BaseResultWithData


class ProductBulkImportCommand:
    @staticmethod
    def execute(request):
        
        if not isinstance(request.data, list):
            return BaseResultWithData(
                message="Invalid data format. Expected a list of products.",
                status_code=HTTPStatus.BAD_REQUEST
            )

        created_count = 0
        errors = []

        for idx, item in enumerate(request.data):
            serializer = ProductImportSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({
                    "index": idx,
                    "errors": serializer.errors
                })

        return BaseResultWithData(
            data={
                "created_count": created_count,
                "errors": errors
            },
            message="Product bulk import completed.",
            status_code=HTTPStatus.OK
        )