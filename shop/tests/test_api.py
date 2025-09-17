import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from shop.models import Product

@pytest.mark.django_db
def test_register_and_login():
    client = APIClient()
    # регистрация бота
    resp = client.post(reverse("register"), {"username":"u1","email":"u1@e.com","password":"password123"}, format="json")
    assert resp.status_code == 201
    # логин
    resp = client.post(reverse("token_obtain_pair"), {"username":"u1","password":"password123"}, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data

@pytest.mark.django_db
def test_products_list_search_and_detail():
    Product.objects.create(name="Phone X", price="999.00", description="Flagship")
    Product.objects.create(name="Case", price="19.99", description="Accessory")
    client = APIClient()
    resp = client.get("/api/products/?q=phone")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict) and "results" in data
    assert any("Phone X" in p["name"] for p in data["results"])
    pid = data["results"][0]["id"]
    resp = client.get(f"/api/products/{pid}/")
    assert resp.status_code == 200

@pytest.mark.django_db
def test_cart_and_order_flow():
    p = Product.objects.create(name="P1", price="10.00")
    u = User.objects.create_user(username="u2", password="password123")
    client = APIClient()
    tok = client.post(reverse("token_obtain_pair"), {"username":"u2","password":"password123"}, format="json").data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
    # добавить в корзину
    resp = client.post("/api/cart/add/", {"product_id": p.id, "quantity": 2}, format="json")
    assert resp.status_code == 201
    # содержимое корзины
    resp = client.get("/api/cart/")
    assert resp.status_code == 200
    assert resp.data[0]["quantity"] == 2
    # новый ордер
    resp = client.post("/api/orders/create_order/")
    assert resp.status_code == 201
    assert str(resp.data["total"]) == "20.00"
