from django.contrib import admin
from .models import Product, CartItem, Order, OrderItem


admin.site.register([Product, CartItem, Order, OrderItem])
