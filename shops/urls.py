from django.urls import path

from .views import SellerShopAPIView


urlpatterns = [
    path(
        "my-shop/",
        SellerShopAPIView.as_view(),
        name="seller-my-shop",
    ),
]