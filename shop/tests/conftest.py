import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from shop.models import Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_factory(db):
    def _make(count=3, **overrides):
        made = []
        for i in range(count):
            data = {
                "name": overrides.get("name", f"Product {i+1}"),
                "price": Decimal(str(overrides.get("price", i + 1))),
                "description": overrides.get("description", f"Desc {i+1}"),
            }
            if "image" in overrides:
                data["image"] = overrides["image"]
            made.append(Product.objects.create(**data))
        return made
    return _make
