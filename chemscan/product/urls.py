
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('product/<str:barcode>/', views.product_details, name='product_details'),
    path('fetch/', views.fetch_product_details, name='fetch_product_details'),
    path('', views.index, name='index'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
