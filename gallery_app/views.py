from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Painting, CartItem
import uuid
import base64
import hashlib
import hmac
import json
from django.utils.timezone import now
# Home View
def home(request):
    return render(request, 'home.html')

# Gallery View

def gallery(request):
    query = request.GET.get('q', '')  # Search query
    category_filter = request.GET.get('category', '')  # Category filter
    price_min = request.GET.get('price_min', '')  # Minimum price
    price_max = request.GET.get('price_max', '')  # Maximum price
    released_date = request.GET.get('released_date', '')  # Released date filter

    paintings = Painting.objects.all()

    # Apply search only if there is a query
    if query:
        paintings = paintings.filter(name__icontains=query)

    # Apply category filter if selected
    if category_filter:
        paintings = paintings.filter(category=category_filter)

    # Apply price range filter
    if price_min:
        paintings = paintings.filter(price__gte=price_min)
    if price_max:
        paintings = paintings.filter(price__lte=price_max)

    # Apply released date filter
    if released_date:
        paintings = paintings.filter(released_date=released_date)

    # Organize paintings into categories
    categories = {
        "Bookmark": paintings.filter(category="Bookmark"),
        "Landscape": paintings.filter(category="Landscape"),
        "Portrait": paintings.filter(category="Portrait"),
        "Sketch": paintings.filter(category="Sketch"),
    }

    return render(request, 'gallery.html', {
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
        'price_min': price_min,
        'price_max': price_max,
        'released_date': released_date,
    })

# Add to Cart
@login_required(login_url='/auth/login/')
def add_to_cart(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, painting=painting, status="unpaid")

    if not created:
        # Increment the quantity if the item is already in the cart
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"The quantity of {painting.name} has been updated.")
    else:
        messages.success(request, f"{painting.name} added to your cart!")
    
    return redirect('gallery')

# View Cart (only unpaid items)
@login_required(login_url='/auth/login/')
def my_cart(request):
    cart_items = CartItem.objects.filter(user=request.user, status="unpaid")
    total_price = sum(item.painting.price * item.quantity for item in cart_items)
    secret_key = "8gBm/:&EnhH.1/q"
    uid = uuid.uuid4()
    message = f"total_amount={total_price},transaction_uuid={uid},product_code=EPAYTEST"
    hmac_sha256 = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        "uuid": uid,
        "signature": signature,
    }
    return render(request, 'my_cart.html', context)

# Remove from Cart
@login_required(login_url='/auth/login/')
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, f"{cart_item.painting.name} has been removed from your cart.")
    return redirect('my_cart')

# Clear Cart
@login_required(login_url='/auth/login/')
def clear_cart(request):
    CartItem.objects.filter(user=request.user, status="unpaid").delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect('my_cart')

# My Orders
@login_required(login_url='/auth/login/')
def my_orders(request):
    orders = CartItem.objects.filter(user=request.user, status__in=["paid", "unpaid(COD)"])
    context = {'orders': orders}
    return render(request, 'my_orders.html', context)

@login_required(login_url='/auth/login/')
def payment_success(request):
    # Get the 'data' from the URL query parameter
    data = request.GET.get('data', None)
    
    if data:
        # Decode the data
        try:
            decoded_data = base64.b64decode(data).decode('utf-8')
            map_data = json.loads(decoded_data)
            
            # Check the payment status
            if map_data.get("status") == "COMPLETE":
                # Payment is successful, update the order status to "paid"
                CartItem.objects.filter(user=request.user, status="unpaid").update(status="paid")
                messages.success(request, "Payment received successfully.")
            else:
                # Payment failed, notify the user and return to the cart
                messages.error(request, "Payment failed. Please try again.")
                return redirect('my_cart')
        except (base64.binascii.Error, json.JSONDecodeError) as e:
            # Handle decoding errors
            messages.error(request, "There was an error processing the payment data.")
            return redirect('my_cart')
    else:
        # If no data is provided in the query string
        messages.error(request, "No payment data received.")
        return redirect('my_cart')

    return render(request, "payment_success.html")

@login_required(login_url='/auth/login/')
def cod_checkout(request):
    cart_items = CartItem.objects.filter(user=request.user, status="unpaid")

    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Add items before placing an order.")
        return redirect('my_cart')

    # Mark all cart items as "paid" but keep delivery as "pending"
    for item in cart_items:
        item.status = "unpaid(COD)"  # Payment is not yet received
        item.delivery = "pending"  # Default delivery status
        item.added_at = now()  # Set order time
        item.save()

    messages.success(request, "Your order has been placed with Cash on Delivery.")
    return redirect('my_orders')