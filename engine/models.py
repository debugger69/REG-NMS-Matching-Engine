from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, model_validator
import uuid

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    IOC = "ioc"
    FOK = "fok"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: Decimal
    price: Decimal | None = None
    stop_price: Decimal | None = None
    take_profit_price: Decimal | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Decimal: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
        
    @model_validator(mode="after")
    def check_valid_order(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValueError('Order quantity must be positive')
        if self.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.TAKE_PROFIT] and (self.price is None or self.price <= 0):
            raise ValueError('Order price must be positive for limit/stop/take-profit orders')
        return self

class Trade(BaseModel):
    trade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    price: Decimal
    quantity: Decimal
    aggressor_side: OrderSide
    maker_order_id: str
    taker_order_id: str
    maker_fee: Decimal = Decimal("0")
    taker_fee: Decimal = Decimal("0")
    fee_currency: str = "USDT"