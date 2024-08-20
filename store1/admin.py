from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Carsuol
from .models import OrderImages,Faq,RazorpayPayment,ContactVendor
class CarsuolAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image')

class OrderImageAdming(admin.ModelAdmin): 
    list_display=('order_id','product_id','image','user_id','user_description')

class FaqDetails(admin.ModelAdmin): 
    list_display=('faq_title','faq_description')
class payment(admin.ModelAdmin): 
    list_display=('razorpay_order_id','payment_id','signature','order_id')
class ContactShop(admin.ModelAdmin): 
    list_display=('first_name','last_name','email','phone_number','message')

admin.site.register(RazorpayPayment,payment)
admin.site.register(Carsuol, CarsuolAdmin)
admin.site.register(OrderImages,OrderImageAdming) 
admin.site.register(Faq,FaqDetails)
admin.site.register(ContactVendor,ContactShop)