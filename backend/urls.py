from django.contrib import admin
from django.urls import path,include
from django.apps import apps
from store1 import urls
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from store1.api_razorpay import RazorpayOrderAPIView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.

    path('admin/', admin.site.urls),
    
     path("api/", include("oscarapi.urls")),

    path("apiv2/", include('store1.urls')),

    path('', include(apps.get_app_config('oscar').urls[0])),
    path('api/createOrder/',RazorpayOrderAPIView.as_view()),
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)