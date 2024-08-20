from .razorpay.main import RazorpayClient
from rest_framework.decorators import APIView
from .seralizers import RazorpayOrderSerializer
from rest_framework.response import Response
from rest_framework import status

rz_client = RazorpayClient()

class RazorpayOrderAPIView(APIView):
    """This API will create an order"""
    
    def post(self, request):
        razorpay_order_serializer = RazorpayOrderSerializer(
            data=request.data
        )
        if razorpay_order_serializer.is_valid():
            order_response = rz_client.create_order(
                amount=razorpay_order_serializer.validated_data.get("amount"),
                currency=razorpay_order_serializer.validated_data.get("currency")
            )
            response = {
                "status_code": status.HTTP_201_CREATED,
                "message": "order created",
                "data": order_response
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": razorpay_order_serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
