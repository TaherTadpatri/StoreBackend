from django.db import models
from oscar.core.loading import get_model

# Create your models here.
product=get_model('catalogue','product')
Order =get_model('order','order')
User=get_model('auth','user')

class Carsuol(models.Model): 
    title=models.CharField(max_length=100) 
    description=models.TextField()
    link=models.URLField()
    image=models.ImageField() 


    
class OrderImages(models.Model):
    order_id=models.IntegerField(blank=True) 
    image=models.ImageField(upload_to='order_images')
    user_description=models.TextField(blank=True) 
    user_id=models.CharField(max_length=10) 
    product_id =models.CharField(max_length=10)

class Otp(models.Model): 
    user_id=models.CharField(max_length=10)
    otp=models.CharField(max_length=10)
    created_at=models.DateTimeField(auto_now_add=True)
    expire=models.DateField()

class Faq(models.Model): 
    faq_title=models.CharField(max_length=299) 
    faq_description=models.TextField() 


class RazorpayPayment(models.Model): 
    razorpay_order_id = models.CharField(max_length=256)
    payment_id = models.CharField(max_length=256)
    signature=models.CharField(max_length=256)
    order_id=models.ForeignKey(Order, on_delete=models.CASCADE)


class ContactVendor(models.Model): 
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    email=models.EmailField()
    phone_number=models.CharField(max_length=20)
    message=models.TextField()
    
class Transaction(models.Model):
    payment_id = models.CharField(max_length=200, verbose_name="Payment ID")
    order_id = models.CharField(max_length=200, verbose_name="Order ID")
    signature = models.CharField(max_length=500, verbose_name="Signature", blank=True, null=True)
    amount = models.IntegerField(verbose_name="Amount")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)