from django.urls import path
from .views import home,gallery,add_to_cart,my_cart,remove_from_cart,clear_cart

urlpatterns = [
    path('', home, name='home'),
    path('gallery', gallery, name='gallery'),
    path('add_to_cart/<int:painting_id>/', add_to_cart, name='add_to_cart'),
    path('my_cart/', my_cart, name='my_cart'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', clear_cart, name='clear_cart'),
]
