from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
	path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('restore',views.mip, name='restore'),
    path('enhance',views.rghs, name='enhance'),
    path('enhanced',views.get_image_rghs, name='getimageEnhance'),
    path('restored',views.get_image_mip, name='getimageRestore'),
    path('classify',views.classify, name='classify'),
    path('predict',views.classifyimage, name='classifyimage'),
    path('about-us',views.about, name='about'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
