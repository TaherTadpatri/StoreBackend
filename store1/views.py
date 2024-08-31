from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from .seralizers import *
from .models import * 
from oscar.core.loading import get_model
import requests
import json
from oscar.apps.basket.models import Basket
from django.contrib.auth.models import User  

from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions
from oscarapi.utils.loading import get_api_class
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import MultiPartParser, FormParser
import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from oscar.apps.checkout.mixins import OrderPlacementMixin
import string 
from .razorpay.main import RazorpayClient
from oscarapi.serializers.product import ProductSerializer
from oscarapi.basket.operations import get_basket

basket=get_model('basket','basket')
Lines=get_model('basket','line')
product=get_model('catalogue','product')
userAddress=get_model('address','useraddress')
productcatgoery=get_model('catalogue','productcategory') 
BasketLine=get_model('basket','line')


"""
    get caursol items 

"""
@csrf_exempt
@api_view(['GET'])
def caursol(request): 
    if request.method == 'GET':
        carousel_items = Carsuol.objects.all() 
        print(carousel_items) # Query all carousel items    
        serializer = CarouselItemAdminSerializer(carousel_items, many=True)  # Serialize multiple item
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return Response (status=status.HTTP_405_METHOD_NOT_ALLOWED)


"""
   get products of specific cateogry or by using the category id

"""
        

@api_view(['POST'])
def getcatproduct(request): 
     if request.method == 'POST':
        catid = int(request.data.get('category_id'))
        products_in_category = productcatgoery.objects.filter(category_id=catid)
        products=[]
        if products_in_category.exists():   
            for product_item in products_in_category:
                product_id = product_item.product_id  # Get the product ID from the first category
                Product_item = product.objects.filter(id=product_id)  # Filter Products based on the retrieved ID
                serializer = ProductSerializer(Product_item, context={'request': request}, many=True)
                data=serializer.data[0]
                products.append(data)
            return Response(products, status=status.HTTP_200_OK)
        else:
            # Handle the case where no products are found in the category
            return Response(products,status=status.HTTP_200_OK)
     return Response({"message":"something went wrong"},status=status.HTTP_400_BAD_REQUEST)
      
          
     

"""catid=int(request.data.get('category_id'))
          Product = get_model('catalogue', 'Product')      
          products=Product.objects.filter(categories=catid)
          data=[]
          for product in products: 
               url=f'https://storebackend-production-9a2b.up.railway.app/api/products/{product.id}/'
               response = requests.get(url)
               if response.ok:
                   data.append(response.json())
               else: 
                   pass
             #data=Productcatseralizer(data,many=True)"""
"""
   check pincode service available or not using the shiprocket api 
   and the api shiprocket token expires every 10 day need to refresh 
   by sending the request to login shiprocket api
"""
@api_view(['POST'])
def checkservice(request): 
     if request.method == 'POST': 
         url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
         token=settings.SHIPROCKET_API
         payload = json.loads(request.body)
         print(payload)
         headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
          }
         response = requests.request("GET", url, headers=headers, json=payload)
         data=response.json()
         print(data)
         return Response(response.json(), status=status.HTTP_200_OK)





@api_view(['GET','POST'])
@permission_classes([permissions.IsAuthenticated])
def home(request):
    return Response({'message': 'Welcome to the home page'}, status=status.HTTP_200_OK)

"""
   product detail for the cart 
   title,description and image 
   
"""
def getParentdata(product_id): 
    parentProduct=product.objects.get(id=product_id) 
    parent_id=parentProduct.parent_id
    url=f'https://storebackend-production-9a2b.up.railway.app/api/products/{parent_id}/'
    response=requests.get(url)
    parentData=response.json()
    return ({'id':product_id,
             'title':parentData['title'],
             'image':parentData['images'][0]['original'],
             })

def getproductdetails(products): 
    data = []
    Prodcut=get_model('catalogue','product')

    for item in products: 
        productid=item['product']
    
        url=f'https://storebackend-production-9a2b.up.railway.app/api/products/{productid}/'
        response=requests.get(url)
        product_data = response.json() 
        ischild=product_data['structure']
        if ischild=="child": 
            parentdata=getParentdata(productid) 
            data.append(parentdata)
        else:
            data.append({'id':product_data['id'], 'title': product_data['title'],'image' : product_data['images'][0]['original']})
    return data
#'image' : product_data['images'][0]['original']
"""
   returns a object of two array one cart items ('product','line') 
    and a array of product description title,image,description 
"""


@permission_classes([permissions.IsAuthenticated])
class Cart(APIView): 
    def get(self,request): 
        lineproducst=[]
        try:
            user_basket=get_object_or_404(basket,owner=request.user,status='Open')
        except basket.MultipleObjectsReturned: 
           
            return Response(lineproducst,status=status.HTTP_200_OK)
       
        if user_basket.num_items > 1:   #checks the status of the basket ,accepts with the only open basket 
            open_basket = Basket.objects.filter(id=user_basket.id, status='Open') 
            if open_basket.exists():
                user_basket=open_basket.first()
            else:
                return Response (lineproducst,status=status.HTTP_200_OK)
       
        if user_basket.is_empty: 
            return Response(lineproducst,status=status.HTTP_200_OK) 
   
        user_lines=user_basket.all_lines()
        for line in user_lines:
            product = line.product
            product_images = product.images.all()
            if product_images.exists():
                images = product_images.values('original')
            else:
                parent_product = product.parent
                if parent_product:
                    images = parent_product.images.all().values('original')
                else:
                    images = [] 
            lineproducst.append({ 
                "title":product.title,
                "quantity":line.quantity,
                "price":line.price_incl_tax,
                "images": [f"{settings.MEDIA_URL}{image['original']}" for image in images],
                "basket_id":user_basket.id
            }) 
      
        return Response(lineproducst,status=status.HTTP_200_OK)
    

    def post(self,request): 
        try: 
            product_id=request.data.get('product_id') 
            if not product_id: 
                return Response({"error": "missing product_id field"} ,status=status.HTTP_400_BAD_REQUEST)
            product_object=product.objects.get(id=product_id)
            user_basket = get_basket(request)
            quantity=request.data.get('quantity') 
            user_basket.add_product(product_object,quantity=quantity)
            user_basket.save() 
            return Response({"message":"product added sucessfully"},status=status.HTTP_200_OK)
        except ObjectDoesNotExist: 
            return Response({"error": "product or basket not found"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            return Response({"error": f'an error occured {str(e)}'},status=status.HTTP_400_BAD_REQUEST)


            
            

    

            

        


    
    
"""
  add product to the cart and if the product is already in the
  cart then increase the quantity of the product in the cart
"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addProductToCart(request): 
    if request.method == 'POST': 
        user_id = request.user.id
        basket_id=basket.objects.get(owner_id=user_id)
        basket_id=basket_id.id
        product_id=request.data['product_id']
        
        quantity=int(request.data['quantity'])
        url=f'https://storebackend-production-9a2b.up.railway.app/api/products/{product_id}/stockrecords/'
        response = requests.get(url)
        print(response.text)
        stock_data = response.json()
        if int(stock_data[0]['num_in_stock']) >= quantity:
            try:
                stockrecord_id=stock_data[0]['id']
                line_reference=str(product_id)+ "_" +str(stockrecord_id)
                price=stock_data[0]['price']
                price_currency=stock_data[0]['price_currency']
                print(product_id,stockrecord_id,basket_id)
                try:
                    #cartobj=get_object_or_404(Cart,product_id=product_id,basket_id=basket_id)
                    cartobj=Cart.objects.get(product_id=product_id,basket_id=basket_id)
                    print('working')
                    if cartobj: 
                        oldquantity=cartobj.quantity
                        newquantity=oldquantity+quantity
                        cartobj.quantity=newquantity
                        cartobj.save()
                        return Response({'message': 'quantity added'},status=status.HTTP_200_OK)
                except Cart.DoesNotExist: 
                    Cart.objects.create(line_reference=line_reference,
                                    basket_id=basket_id,
                                    product_id=product_id,
                                    quantity=quantity,
                                    stockrecord_id=stockrecord_id,
                                    price_incl_tax=price,
                                    price_currency=price_currency)
                    return Response({'message' : 'product added to cart'},status=status.HTTP_200_OK)
            except product.DoesNotExist:
                return Response({'error' : 'product not found'},status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'something went wrong'},status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateCart(request): 
    if request.method == 'POST': 
        basket=get_basket(request) 
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity'))
        try:
            line = BasketLine.objects.get(basket=basket, product_id=product_id)
        except BasketLine.DoesNotExist:
            return Response({'error': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        line.quantity = quantity
        line.save()
        return Response({'message': 'quantity updated'}, status=status.HTTP_200_OK)
        """cartItem=request.data['cart']
        cartdata=[]
        print(cartItem)
        for product in cartItem: 
            cart_id=product['id']
            quantity=product['quantity']
            print(cart_id) 
            print(quantity)
            if quantity == 0: 
                try: 
                    cartobj=Cart.objects.get(id=cart_id)
                    cartobj.delete()
                except Cart.DoesNotExist:
                    print('product not found')
            else: 
                try:
                    cartobj=Cart.objects.get(id=cart_id)
                    cartobj.quantity=quantity
                    cartobj.save()
                    cartitemdata=cartproductseralizer(cartobj,many=False) 
                    cartdata.append(cartitemdata.data)
                except Cart.DoesNotExist:
                    pass
        return Response({"cart": cartdata}, status=status.HTTP_200_OK)"""

country=get_model('address','country') 
@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def getuserAddress(request): 
    if request.method== 'GET': 
        user_id=request.user.id    
        print(user_id)
        try: 
            useraddress=userAddress.objects.get(user_id =user_id) 
            useraddress=userAddressSeralizer(useraddress,many=False) 
            return Response({"formdata": useraddress.data} ,status=status.HTTP_200_OK) 
        except ObjectDoesNotExist:
            usercountry=country.objects.get(name='india')
            newuserAddress=userAddress.objects.create(user_id=user_id,country=usercountry)
            useraddress=userAddressSeralizer(newuserAddress,many=False)
            return Response({"formdata": useraddress.data},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
    return Response({ 'error' : 'something went wrong' } ,status=status.HTTP_400_BAD_REQUEST)
        

def update_or_create_user_address(user_address_data):
    user_id = user_address_data.pop('user_id')  # Extract user_id

    try:
        user_address = userAddress.objects.get(user=user_id)
        serializer = userAddressSeralizer(user_address, data=user_address_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"formdata": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 

    except userAddress.DoesNotExist:
        serializer = userAddressSeralizer(data=user_address_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"formdata": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 

 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateUserAddress(request):
    if request.method == 'POST':
        user_address_data = request.data['formData']
        print(user_address_data)
        user_id =request.user.id
        user_address = userAddress.objects.get(user=user_id)
        serializer = userAddressSeralizer(user_address, data=user_address_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"formdata": serializer.data}, status=status.HTTP_200_OK)
        else: 
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({'message' : 'something went wrong'} , status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CustomOrderImages(request): 
    parser_classes = (MultiPartParser, FormParser)
    if request.method == 'POST':
        ser=CustomImageSeralizer(data=request.data) 
        if ser.is_valid(): 
            ser.save()
            return Response({"formdata": ser.data}, status=status.HTTP_201_CREATED)

        
    return Response(status=status.HTTP_400_BAD_REQUEST) 
        

class customImages(APIView): 
    parser_classes = (MultiPartParser, FormParser)
    def post(self,request): 
        data=request.FILES()
        post_seralizer=CustomImageSeralizer(data=request.data,many=False)
        if post_seralizer.is_valid(): 
            post_seralizer.save()
            return Response({'message' : "image uploaded sucessfully"} ,status=status.HTTP_200_OK)
        return Response({'message' : "error"} ,status=status.HTTP_400_BAD_REQUEST)
    

class Otps(APIView): 
    def post(self,request):
        user_email=request.data['user_email']
        db_user=User.objects.filter(email=user_email).first()
        print(db_user)
        if db_user:
            userExist=Otp.objects.filter(user_id=db_user.id) 
            print(userExist)
            if userExist.exists():
                userExist.delete() 
            otp = random.randint(100000, 999999)
            expire= datetime.now() + timedelta(minutes=5)
            Otp.objects.create(user_id=db_user.id,otp=otp,expire=expire)
            subject = 'Otp request for changing password'
            message = f"""
                Dear {db_user.username},

                You have requested to change your password. 
                Your OTP is: {otp}

                This OTP is valid for {expire.strftime("%Y-%m-%d %H:%M:%S")} minutes.

                Please do not share this OTP with anyone.

                

                Sincerely,
                T M Taher
                shafiphotostudio@gmail.com
                whatsapp support : +916361002427
            """ 
            from_email = settings.EMAIL_HOST_USER
            to=user_email 
            try:
                send_mail(subject, message, from_email, [to], fail_silently=False)
            except Exception as e: 
                return Response({"error": "unable to send email"} ,status=status.HTTP_400_BAD_REQUEST
                                )
            return Response ({ 'message' : "username exist",
                              'email' : user_email,
                              'expire_at': expire.strftime("%Y-%m-%d %H:%M:%S")} ,status= status.HTTP_200_OK)
        return Response({"message" : " username does not exist"} , status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])        
def validateOtp(request): 
    if request.method == 'POST':
        user_email=request.data['user_email']
        otp=request.data['otp']
        db_user=User.objects.filter(email=user_email).first()
        if db_user:
            userExist=Otp.objects.filter(user_id=db_user.id).first()
            print(userExist.otp)
            if userExist.otp==otp: 
                return Response({"message" : "otp is valid"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : " " , "error" : "invalid otp enter correct otp"},status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['POST']) 
def ChangePassword(request): 
    if request.method == 'POST': 
        user_email=request.data.get('email') 
        user=User.objects.filter(email=user_email) 
        if user.exists(): 
            user=user.first()
            new_password=request.data.get('new_password')
            confirm_password=request.data.get('confirm_password')
            if new_password == confirm_password : 
                user.set_password(new_password) 
                user.save() 
                return Response({"message": "password changed sucessfully "} ,status=status.HTTP_200_OK)
            else: 
                return Response({"error" : "password is not same"} ,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def search(request): 
    if request.method=="POST": 
        search_query=request.data.get('search') 
        search_products=product.objects.filter(
             Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        data=[]
        for item in search_products: 
            url=f'https://storebackend-production-9a2b.up.railway.app/api/products/{item.id}/'
            response=requests.get(url)
            productData=response.json()
            data.append(productData)       
        print(data)
        return Response(data, status=status.HTTP_200_OK)
    return Response({"error":"something went wrong"} ,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET']) 
def faqDetails(request): 
    if request.method == 'GET': 
        faq=Faq.objects.all()
        ser=FaqSeralizer(faq,many=True) 
        return Response(ser.data,status=status.HTTP_200_OK)
    return Response({"message":"something went wrong"} ,status=status.HTTP_400_BAD_REQUEST)

def generate_order_number():
    """Generates a unique order number."""

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    order_number = f"ORDER-{timestamp}-{random_part}"
    return order_number

def storeRazorpayDetail(razorPayDetails,order): 
    try:
        payment=RazorpayPayment.objects.create(
             razorpay_order_id=razorPayDetails['razorpay_order_id'],
            payment_id=razorPayDetails['payment_id'],
            signature=razorPayDetails['signature'],
            order=order,
        )
        return payment
    except Exception as e: 
        return e
paymentSource=get_model('payment','source')
transcation=get_model('payment','transaction')
def createPaymentEvent(paymentDetails,order_total,order): 
    even_type='razorpay'
    amount=order_total['total']
    currency='INR'
    amount_allocted=order_total['excl_tax']
    amount_debited=order_total['excl_tax']
    amount_refunded=0
    order_id=order.id
    label='razorpay amount'
    source_type_id=1
    refernce=paymentDetails['order_id']
    payment_source=paymentSource.objects.create(
        #even_type=even_type,
        #amount=amount,
        currency=currency,
        amount_allocated=amount_allocted,
        amount_debited=amount_debited,
        amount_refunded=amount_refunded,
        label=label,
        order_id=order_id,
        source_type_id=source_type_id,
        reference=refernce,
    )
    print('successfull')
    txn_type='razorpay'
    amount=order_total['excl_tax']
    refernce=paymentDetails['order_id']
    status='paid'
    source_id=1
    """payment_transaction=transcation.objects.create( 
        txn_type=txn_type,  
        amount=amount,
        reference=refernce,
        status=status,
        source_id=payment_source.source_type_id
    )"""
    

    
    
ShippingAddres=get_model('order','shippingaddress') 
BillingAddress=get_model('order','billingaddress')
Orders=get_model('order','order')  
Country=get_model('address','country')
OrderLine=get_model('order','line') 
StockRecord=get_model('partner','stockrecord')
@permission_classes([IsAuthenticated])
class Checkout(APIView): 
    def post(self,request): 
        userbasket = Basket.objects.get(owner_id=request.user.id)
        shipping_address = request.data['shipping_address']
        billing_address = request.data['billing_address']
        shipping_method = request.data['shipping_method']
        #guest_email = request.data['guest_email']
        order_total = request.data['order_total']
        shipping_charge=request.data['shipping_charge']
        
        country_name = "india"
        total_excl = order_total['excl_tax']
        country = Country.objects.filter(name=country_name)[0]

        razorpay_details=request.data['payment_details']
        
        shipping_address_obj = ShippingAddres.objects.create(
            **shipping_address,
            country=country
        )
        billing_address_obj = BillingAddress.objects.create(
            **billing_address,
              country=country  
        )
        order_number=100000+userbasket.id
        """details=RazorpayClient.verify_payment_signature(self,razorpay_order_id=razorpay_details['payment_id'],
                                                    razorpay_payment_id=razorpay_details['order_id'],
                                                    razorpay_signature=razorpay_details['signature'])
        print(details)"""
        order=Orders.objects.create(
                user_id=request.user.id,
                number=order_number,
                currency="INR",
                total_incl_tax =total_excl,
                total_excl_tax=total_excl,
                #total_excl =total_excl,
                shipping_code='123',
                shipping_incl_tax=shipping_charge["excl_tax"],
                shipping_address=shipping_address_obj,
                billing_address=billing_address_obj,
                shipping_method=shipping_method,
                #guest_email=guest_email ,
                basket=userbasket,
                status=settings.OSCAR_INITIAL_ORDER_STATUS
            )
        print(order.id)
        order_lines=[]
        basketLines=userbasket.lines.all() 
        print(basketLines) 
        for line in basketLines:
            product_item=product.objects.get(id=line.product_id )
            stockrecord_item=StockRecord.objects.get(id=line.stockrecord_id)
         
            OrderLine.objects.create(
                product=product_item,
                title=product_item.title,
                upc=product_item.upc,
                quantity=line.quantity,
                line_price_incl_tax=line.quantity * line.price_incl_tax,
                line_price_excl_tax=line.quantity * line.price_incl_tax,
                unit_price_incl_tax=line.price_incl_tax,
                unit_price_excl_tax=line.price_incl_tax,
                line_price_before_discounts_incl_tax=line.price_incl_tax,
                line_price_before_discounts_excl_tax=line.price_incl_tax,
                status=settings.OSCAR_INITIAL_LINE_STATUS,
                order=order, 
                partner_id=stockrecord_item.partner_id,
                stockrecord_id=line.stockrecord_id,
                )
        payment=storeRazorpayDetail(razorpay_details,order)
        createPaymentEvent(razorpay_details,order_total,order)
        userbasket.delete()
                        
        

        # Create a new order
        """order = OrderPlacementMixin().place_order(
            order_number=OrderPlacementMixin().generate_order_number(userbasket),
            user=request.user,
            basket=userbasket,
            shipping_address=shipping_address_obj,
            shipping_method=shipping_method,
            shipping_charge=0,
            billing_address=billing_address_obj,
            order_total =order_total,
            curreny='INR',
            guest_email=guest_email
        )"""
        return Response({"message" :"Order created sucessfully"},status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrders(request): 
    user_id =request.user.id
    print(user_id)
    orders = Order.objects.filter(user_id=user_id)
    print(orders)
    if orders.exists():
        order_data = []
        for order in orders:
            order_lines = OrderLine.objects.filter(order=order)
            product_data = []
            for order_line in order_lines:
                url = f'https://storebackend-production-9a2b.up.railway.app/api/products/{order_line.product_id}/'
                response = requests.get(url)
                data=response.json()
                if data['structure']=='child': 
                    parentdata=getParentdata(order_line.product_id) 
                    product_data.append(parentdata)
                else:
                    product_data.append(data)

                order_data.append({
                    "order": order.id,
                    "order_number": order.number,
                    "order_date": order.date_placed,
                    "order_total": order.total_excl_tax,
                    #"order_quantity" :order.quanitity, design afterwards 
                    "status" : order.status,
                    "product_id": product_data[0]["id"],
                    "product_title": product_data[0]["title"],
                    "product_image": product_data[0]["image"]
                })
        return Response({'orders': order_data}, status=status.HTTP_200_OK)
    else:
        return Response({'orders': ""}, status=status.HTTP_200_OK)

@api_view(['POST'])
def ContactUs(request):
    if request.method == 'POST':
        print(request.data)
        ser=ContactVendorSeralizer(data=request.data.get('form'))
        if ser.is_valid(): 
            ser.save()
            return Response({'message': 'Your message has been sent'}, status=status.HTTP_200_OK)
        else: 
            return Response({'message': ser.error_messages}, status=status.HTTP_400_BAD_REQUEST)
    else: 
        return Response({"error": "something went wrong" },status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getUserDetails(request): 
    if request.method == 'GET': 
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        return Response({'user': user.username,
                         'email' : user.email}, status=status.HTTP_200_OK)
    return Response({'message' : "something went wrong"},status=status.HTTP_200_OK)