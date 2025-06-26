import pytest
from engine.matching_engine import MatchingEngine
from engine.models import Order, OrderType, OrderSide
from decimal import Decimal

@pytest.fixture
def engine():
    return MatchingEngine()

def test_invalid_order_type(engine):
    with pytest.raises(Exception):
        Order(
            symbol="BTC-USDT",
            order_type="invalid_type",  # Invalid
            side=OrderSide.BUY,
            quantity=Decimal("1.0"),
            price=Decimal("50000.0")
        )

def test_negative_quantity(engine):
    with pytest.raises(Exception):
        Order(
            symbol="BTC-USDT",
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            quantity=Decimal("-1.0"),  # Negative quantity
            price=Decimal("50000.0")
        )

def test_missing_required_fields(engine):
    with pytest.raises(Exception):
        Order(
            symbol="BTC-USDT",
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            quantity=None,  # Missing quantity
            price=Decimal("50000.0")
        )
