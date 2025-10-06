from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Product, Category, Order, OrderItem
import pdfkit

# Show all products and categories
def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, "shop/product_list.html", {"categories": categories, "products": products})

# Add to cart via session
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    request.session['cart'] = cart
    return redirect('cart')

# Remove from cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')

# Cart page
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        subtotal = product.price * qty
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
        total += subtotal
    return render(request, "shop/cart.html", {"cart_items": cart_items, "total": total})

# Checkout page with UPI QR
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        subtotal = product.price * qty
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
        total += subtotal

    if request.method == 'POST':
        # Manual "confirm payment" button pressed by user
        order = Order.objects.create(user=request.user, total=total)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['subtotal'],
            )
        request.session['cart'] = {}  # clear cart
        return redirect('payment_success')
    # Show checkout with QR
    return render(request, "shop/checkout.html", {"cart_items": cart_items, "total": total})

# Payment success page
@login_required
def payment_success(request):
    return render(request, "shop/payment_success.html")

# Order history page
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, "shop/order_history.html", {"orders": orders})

# GST Invoice as PDF or HTML
@login_required
def invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    html = render_to_string("shop/invoice.html", {"order": order})
    try:
        pdf = pdfkit.from_string(html, False)
        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response
    except Exception:
        # fallback to HTML if PDF not available
        return HttpResponse(html)

