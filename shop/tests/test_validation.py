import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_validation_error_returns_422():
    client = APIClient()
    # создание товара без прав админа
    resp = client.post("/api/products/", {"name": ""}, format="json")
    assert resp.status_code in (400, 401, 403)  # сначала может быть 401/403
    # добавление в корзину без товара
    resp = client.post("/api/cart/add/", {"quantity": 1}, format="json")
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data and "detail" in data["error"]

def test_products_search_and_ordering(api_client, product_factory):
    product_factory(name="Phone X", price="999.00")
    product_factory(name="Case", price="19.00")
    r = api_client.get("/api/products/?search=phone")
    assert r.status_code == 200
    names = [it["name"] for it in r.json()["results"]]
    assert "Phone X" in names

    r = api_client.get("/api/products/?ordering=-price")
    assert r.status_code == 200
    items = r.json()["results"]
    assert float(items[0]["price"]) >= float(items[1]["price"])
