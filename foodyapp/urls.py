from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .import views
urlpatterns=[
    path("",views.Home,name="home-page"),
    path("contact/",views.Contact,name="contact-page"),
    path("product/",views.Products_views,name="product-page"),
    path("product/<int:pk>",views.product_detail,name="product-details"),
    path("about/",views.About,name="about-page"),
    path("register/",views.register,name="register-page"),
    path("login/",views.login_view,name="login-page"),
    path("logout/",views.logout_page,name="logout"),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    
