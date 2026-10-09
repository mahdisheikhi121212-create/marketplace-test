from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/products/",
        include("products.api_urls")
    ),

    path(
        "api/customers/",
        include("customers.api_urls")
    ),

    path(
        "api/auth/",
        include("accounts.api_urls")
    ),

    path(
        "api/cart/",
        include("cart.urls")
    ),

    path(
        "api/addresses/",
        include("addresses.urls")
    ),

    path(
        "api/orders/",
        include("orders.urls")
    ),

    path(
        "api/payments/",
        include("payments.urls")
    ),

    path(
        "api/inventory/",
        include("inventory.urls")
    ),

    path(
        "api/seller/",
        include("shops.urls")
    ),

    path(
        "api/categories/",
        include("categories.urls")
    ),

    path(
        "api/locations/",
        include("locations.urls")
    ),

    path(
        "api/shipping/",
        include("shipping.urls")
    ),
]
