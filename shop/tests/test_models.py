import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from shop.models import Product

@pytest.mark.django_db
def test_product_price_cannot_be_negative():
    product = Product(name="Bad", price=Decimal("-1"))
    with pytest.raises(ValidationError):
        product.full_clean()  # вызывает встроенные валидаторы модели
