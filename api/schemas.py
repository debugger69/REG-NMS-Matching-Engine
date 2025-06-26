from pydantic import BaseModel
from decimal import Decimal
from engine.models import OrderType, OrderSide

class OrderRequest(BaseModel):
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: Decimal
    price: Decimal | None = None

class MarketDataResponse(BaseModel):
    timestamp: str
    symbol: str
    asks: list[tuple[Decimal, Decimal]]
    bids: list[tuple[Decimal, Decimal]]

class TradeResponse(BaseModel):
    timestamp: str
    symbol: str
    trade_id: str
    price: Decimal
    quantity: Decimal
    aggressor_side: OrderSide
    maker_order_id: str
    taker_order_id: str