from django.urls import path
from . import views

urlpatterns = [
    path('', views.mall_product_list, name='mall'),
]