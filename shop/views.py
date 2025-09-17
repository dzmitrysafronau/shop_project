from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CartItem, Order, OrderItem, Product
from .permissions import IsAdminUserOrReadOnly
from .serializers import (
    AddToCartSerializer,
    CartItemSerializer,
    OrderSerializer,
    ProductSerializer,
    RegisterSerializer,
)
from .tasks import send_order_notification


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    """Фильтрация, поиск, сортировка"""
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["price"]              # ?price=999.00
    search_fields = ["name", "description"]   # ?search=phone
    ordering_fields = ["price", "id", "name"] # ?ordering=price | -price
    ordering = ["id"]

    def get_queryset(self):
        qs = Product.objects.all().order_by("id")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs


class CartViewSet(viewsets.ViewSet):
    """Работа с корзиной текущего пользователя"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        items = CartItem.objects.filter(user=request.user).select_related("product")
        return Response(CartItemSerializer(items, many=True).data)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def add(self, request):
        """Добавить товар в корзину"""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        product = Product.objects.get(id=product_id)
        item, _ = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"quantity": 0},
        )
        item.quantity += quantity
        item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="remove")
    def remove(self, request, pk=None):
        try:
            item = CartItem.objects.get(pk=pk, user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["delete"], url_path=r"remove-by-product/(?P<product_id>\d+)")
    def remove_by_product(self, request, product_id=None):
        deleted, _ = CartItem.objects.filter(user=request.user, product_id=product_id).delete()
        if deleted == 0:
            return Response({"detail": "В корзине нет такого товара"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def create_order(self, request):
        """Создать заказ из всех позиций корзины"""
        items = (
            CartItem.objects
            .select_for_update()
            .filter(user=request.user)
            .select_related("product")
        )
        if not items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total=Decimal("0"))
        total = Decimal("0")
        bulk_items = []

        for it in items:
            price = it.product.price
            total += price * it.quantity
            bulk_items.append(
                OrderItem(order=order, product=it.product, price=price, quantity=it.quantity)
            )

        OrderItem.objects.bulk_create(bulk_items)
        order.total = total
        order.save()
        items.delete()

        try:
            send_order_notification.delay(order.id, request.user.username, str(total))
        except Exception:
            pass

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def my(self, request):
        """Список заказов текущего пользователя"""
        orders = (
            Order.objects.filter(user=request.user)
            .prefetch_related("items__product")
            .order_by("-id")
        )

        data = []
        for o in orders:
            data.append(
                {
                    "id": o.id,
                    "total": str(o.total),
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                    "items": [
                        {
                            "product_id": it.product_id,
                            "product_name": it.product.name,
                            "price": str(it.price),
                            "quantity": it.quantity,
                        }
                        for it in o.items.all()
                    ],
                }
            )
        return Response(data)
