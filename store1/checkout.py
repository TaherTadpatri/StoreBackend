from rest_framework.decorators import APIView
from oscarapi.views.utils import parse_basket_from_hyperlink
class checkout(APIView): 
    def post(self, request):
        basket = parse_basket_from_hyperlink(request.data, format=None)

        
