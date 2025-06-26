import pytest
from decimal import Decimal
from engine.models import Order, OrderType, OrderSide
from engine.matching_engine import MatchingEngine

@pytest.fixture
def engine():
    return MatchingEngine()

def test_limit_order_matching(engine):
    buy_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    sell_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    # Process sell order first (should rest on book)
    engine.process_order(sell_order)
    
    # Process buy order (should match)
    executions = engine.process_order(buy_order)
    
    assert len(executions) == 1
    assert executions[0].quantity == Decimal("1.0")
    assert executions[0].price == Decimal("50000.0")

def test_ioc_order(engine):
    # Add resting sell order
    sell_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=Decimal("0.5"),
        price=Decimal("50000.0")
    )
    engine.process_order(sell_order)
    
    # Create IOC buy order for 1.0
    buy_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.IOC,
        side=OrderSide.BUY,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    executions = engine.process_order(buy_order)
    assert len(executions) == 1
    assert executions[0].quantity == Decimal("0.5")
    assert buy_order.quantity == Decimal("0.5")  # Remaining should be canceled

def test_fok_order(engine):
    # Add resting sell order
    sell_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=Decimal("0.5"),
        price=Decimal("50000.0")
    )
    engine.process_order(sell_order)
    
    # Create FOK buy order for 1.0
    buy_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.FOK,
        side=OrderSide.BUY,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    executions = engine.process_order(buy_order)
    assert len(executions) == 0  # Should not execute at all