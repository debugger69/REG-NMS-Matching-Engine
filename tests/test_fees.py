import pytest
from engine.matching_engine import MatchingEngine
from engine.models import Order, OrderType, OrderSide
from decimal import Decimal

@pytest.fixture
def engine():
    return MatchingEngine()

def test_fee_calculation(engine):
    # Process a buy and sell order to generate a trade
    sell_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    engine.process_order(sell_order)
    buy_order = Order(
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    executions = engine.process_order(buy_order)
    trade = executions[0]
    assert trade.maker_fee > 0
    assert trade.taker_fee > 0