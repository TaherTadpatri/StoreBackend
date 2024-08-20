
from django.urls import path,include
from django.apps import apps
from store1 import views

urlpatterns = [
     path("caursol/",views.caursol),
     path("catproducts/",views.getcatproduct),
     path("checkservice/",views.checkservice),    
     path("cart/",views.view_cart),
     path("home/",views.home),
     path("addToCart",views.addProductToCart),
     path("updateCart",views.updateCart),
     path("getUserAddress/",views.getuserAddress),
     path("updateUserAddress/",views.updateUserAddress),
     path('uploadImages',views.CustomOrderImages),
     path('uploadCustomerimage',views.customImages.as_view()),
     path('getOtp',views.Otps.as_view()),
     path('validateOtp',views.validateOtp),
     path('changePassword',views.ChangePassword),
     path('search',views.search),
     path('faq',views.faqDetails),
     path('checkout',views.Checkout.as_view()),
     path('orders',views.getOrders),
     path('contactus',views.ContactUs),
     path('getUserInformation',views.getUserDetails)
]
