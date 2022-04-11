from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
	path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('mip',views.mip,name='mip'),
    path('rghs',views.rghs,name='rghs'),
    path('enhanceRGHS',views.get_image_rghs,name='getimageRGHS'),
    path('restoremip',views.get_image_mip,name='getimagemip'),
    path('classify',views.classify,name='classify'),
    path('predict',views.classifyimage,name='classifyimage'),
    path('about-us',views.about,name='about'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
