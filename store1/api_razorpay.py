from .razorpay.main import RazorpayClient
from rest_framework.decorators import APIView
from .seralizers import RazorpayOrderSerializer,TranscationModelSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from oscar.core.loading import get_model

rz_client = RazorpayClient()
PaymentEvent=get_model('order','paymentevent') 
Orders=get_model('order','order')

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


class TransactionAPIView(APIView):
    """This API will complete order and save the 
    transaction"""
    
    def post(self, request):
        transaction_serializer = TranscationModelSerializer(data=request.data)
        if transaction_serializer.is_valid():
            rz_client.verify_payment_signature(
                razorpay_payment_id = transaction_serializer.validated_data.get("payment_id"),
                razorpay_order_id = transaction_serializer.validated_data.get("order_id"),
                razorpay_signature = transaction_serializer.validated_data.get("signature")
            )
            #transaction_serializer.save()
            event_type_id = request.data.get('event_type_id')
            oscar_order_id=request.data.get('oscar_order_id')
            try: 
                order=Orders.objects.get(number=oscar_order_id) 
            except  ObjectDoesNotExist: 
                return Response({"message": "order number does not exist"},status=status.HTTP_400_BAD_REQUEST)
            payment_event = PaymentEvent(
                order=order,
                amount=request.data.get('amount'),  # Replace with the actual payment amount
                reference=request.data.get('order_id'),  # Replace with the actual payment reference
                event_type_id=event_type_id
            )
            payment_event.save()    
            response = {
                "status_code": status.HTTP_201_CREATED,
                "message": "transaction created"
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": transaction_serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)