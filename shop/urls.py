from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),           # Home / Product listing
    path('cart/', views.cart, name='cart'),                      # Cart page
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),          # Checkout & payment
    path('payment-success/', views.payment_success, name='payment_success'),
    path('orders/', views.order_history, name='order_history'),  # Order history
    path('invoice/<int:order_id>/', views.invoice, name='invoice'), # Invoice PDF/HTML
]
