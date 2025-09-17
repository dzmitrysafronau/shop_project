from django.urls import include, path
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, ProductViewSet, RegisterView

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("", include(router.urls)),

    # Кэшированная версия списка товаров (30 сек)
    path(
        "products-cached/",
        cache_page(30)(ProductViewSet.as_view({"get": "list"})),
        name="products-cached",
    ),
]
