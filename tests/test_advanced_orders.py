from engine.models import Order, OrderType, OrderSide
from decimal import Decimal
import pytest

@pytest.fixture
def engine():
    from engine.matching_engine import MatchingEngine
    return MatchingEngine()

def test_stop_loss_order(engine):
    # Place stop-loss order
    stop_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.STOP_LOSS,
        side=OrderSide.SELL,
        quantity=Decimal("1.0"),
        stop_price=Decimal("49000.0"),
        price=Decimal("50000.0")
    )
    engine.process_order(stop_order)
    
    # Trigger stop order
    market_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=Decimal("1.0")
    )
    # Process order that moves price below stop level
    # Verify stop order was triggered

def test_stop_limit_order(engine):
    # Place stop-limit order (sell if price drops to 49000, limit 48900)
    stop_limit_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.STOP_LIMIT,
        side=OrderSide.SELL,
        quantity=Decimal("1.0"),
        stop_price=Decimal("49000.0"),
        price=Decimal("48900.0")
    )
    engine.process_order(stop_limit_order)
    # Explicitly update market price to trigger the stop-limit order
    engine.update_market_price("BTC-USDT", Decimal("49000.0"))
    # Now add a matching buy order at the limit price to allow execution
    buy_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=Decimal("1.0"),
        price=Decimal("48900.0")
    )
    executions = engine.process_order(buy_order)
    assert any(e.price == Decimal("48900.0") for e in executions)

def test_take_profit_order(engine):
    # Place take-profit order (sell if price rises to 51000)
    take_profit_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.TAKE_PROFIT,
        side=OrderSide.SELL,
        quantity=Decimal("1.0"),
        take_profit_price=Decimal("51000.0"),
        price=Decimal("51000.0")
    )
    engine.process_order(take_profit_order)
    # Explicitly update market price to trigger the take-profit order
    engine.update_market_price("BTC-USDT", Decimal("51000.0"))
    # Now add a matching buy order at the take-profit price to allow execution
    buy_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=Decimal("1.0"),
        price=Decimal("51000.0")
    )
    executions = engine.process_order(buy_order)
    assert any(e.price == Decimal("51000.0") for e in executions)
