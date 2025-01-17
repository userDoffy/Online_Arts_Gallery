import base64
import hashlib
import hmac
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Painting, CartItem
import uuid
# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
def gallery(request):
    categories = {
        "Bookmark": Painting.objects.filter(category="Bookmark"),
        "Landscape": Painting.objects.filter(category="Landscape"),
        "Portrait": Painting.objects.filter(category="Portrait"),
        "Sketch": Painting.objects.filter(category="Sketch"),
    }
    return render(request, 'gallery.html', {'categories': categories})

@login_required
def add_to_cart(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, painting=painting)

    if not created:
        messages.info(request, f"{painting.name} is already in your cart.")
    else:
        messages.success(request, f"{painting.name} added to your cart!")
    
    return redirect('gallery')  # Redirect to the gallery or any page you want

@login_required
def my_cart(request):
    
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.painting.price * item.quantity for item in cart_items)
    secret_key="8gBm/:&EnhH.1/q"
    uid=uuid.uuid4()
    message =  f"total_amount={total_price},transaction_uuid={uid},product_code=EPAYTEST"
    hmac_sha256 = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8') 

    context ={
        'cart_items': cart_items, 
        'total_price': total_price,
        "uuid":uid,
        "signature":signature,
        }
    return render(request, 'my_cart.html', context)

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, f"{cart_item.painting.name} has been removed from your cart.")
    return redirect('my_cart')

@login_required
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect('my_cart')

@login_required
def payment_success(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "Payment Recieved.")
    return render(request,"payment_success.html")