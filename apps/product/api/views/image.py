from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from apps.product.models import ProductImage
from utils.responses import success_deleted_response
from drf_yasg.utils import swagger_auto_schema


class ProductImageView(APIView):
    """
    API endpoint to delete a product image.
    """

    @swagger_auto_schema(
        operation_description="Delete a product image",
        tags=['Product Image'],
        responses={204: 'No content'}
    )
    def delete(self, request, image_id):
        """
        Delete a product image.
        """
        image = get_object_or_404(ProductImage, pk=image_id)
        image.delete()
        return success_deleted_response("Successfully deleted")
