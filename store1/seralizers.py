from rest_framework import serializers
from .models import Carsuol,OrderImages,Otp,Faq,RazorpayPayment,ContactVendor,Transaction
from oscar.core.loading import get_model
from drf_extra_fields.fields import Base64ImageField
from oscar.core.loading import get_model
from oscarapi.serializers.checkout import ShippingAddress,BillingAddress
Basket=get_model('basket','basket')

class CarouselItemAdminSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Allow optional image updates

    class Meta:
        model = Carsuol
        fields = '__all__'  


class Productcatseralizer(serializers.ModelSerializer): 
    class Meta:
        model = get_model('catalogue', 'Product')
        fields = ('id', 'name', 'price', 'image_url')

class cartSeralizers(serializers.ModelSerializer): 
    class Meta: 
        model =get_model('basket','basket')
        fields='__all__'

class cartproductseralizer(serializers.ModelSerializer): 
    class Meta: 
        model=get_model('basket','line') 
        fields='__all__'


class userAddressSeralizer(serializers.ModelSerializer): 
    class Meta: 
        model=get_model('address','useraddress')
        fields='__all__'

class CustomImageSeralizer(serializers.ModelSerializer): 
    #image=serializers.ImageField()
    class Meta:
        model=OrderImages
        filds='__all__'


class OtpSeralizer(serializers.ModelSerializer): 
    class Meta: 
        model=Otp
        fields='[user_id,otp,]'

class FaqSeralizer(serializers.ModelSerializer): 
    class Meta: 
        model=Faq
        fields='__all__'

class RazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField()


class CheckoutSerializer(serializers.Serializer):
    basket = serializers.PrimaryKeyRelatedField(queryset=Basket.objects.all())
    shipping_address = ShippingAddress()
    billing_address = BillingAddress()
    shipping_method = serializers.CharField(max_length=255)
    shipping_code=serializers.CharField()
    total_incl_tax = serializers.DecimalField(max_digits=10, decimal_places=2)

class razorapyModelSeralizer(serializers.ModelSerializer): 
    class Meta: 
        model=RazorpayPayment
        fields='__all__'

class ContactVendorSeralizer(serializers.ModelSerializer): 
    class Meta:
        model=ContactVendor
        fields='__all__'

class TranscationModelSerializer(serializers.ModelSerializer): 
    class Meta:
        model=Transaction
        fields='__all__'