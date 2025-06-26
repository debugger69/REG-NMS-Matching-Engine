import json
from pathlib import Path
from decimal import Decimal
import logging
from collections import deque
from .order_book import OrderBook

class PersistenceManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_order_book(self, symbol: str, order_book: OrderBook):
        try:
            file_path = self.data_dir / f"{symbol}_orderbook.json"
            with open(file_path, 'w') as f:
                data = {
                    "bids": self._serialize_levels(order_book.bids),
                    "asks": self._serialize_levels(order_book.asks),
                    "stop_orders": [self._serialize_order(order) for order in order_book.stop_orders],
                    "take_profit_orders": [self._serialize_order(order) for order in order_book.take_profit_orders]
                }
                json.dump(data, f, default=str)
            self.logger.info(f"Saved order book for {symbol}")
        except Exception as e:
            self.logger.error(f"Failed to save order book: {str(e)}")
    
    def load_order_book(self, symbol: str) -> dict:
        try:
            file_path = self.data_dir / f"{symbol}_orderbook.json"
            if not file_path.exists():
                return None
                
            with open(file_path, 'r') as f:
                data = json.load(f)
                result = {
                    "bids": self._deserialize_levels(data["bids"]),
                    "asks": self._deserialize_levels(data["asks"])
                }
                
                # Handle stop orders and take-profit orders if they exist in the saved data
                if "stop_orders" in data:
                    result["stop_orders"] = [self._deserialize_order(order) for order in data["stop_orders"]]
                else:
                    result["stop_orders"] = []
                    
                if "take_profit_orders" in data:
                    result["take_profit_orders"] = [self._deserialize_order(order) for order in data["take_profit_orders"]]
                else:
                    result["take_profit_orders"] = []
                    
                return result
        except Exception as e:
            self.logger.error(f"Failed to load order book: {str(e)}")
            return None
    
    def _serialize_levels(self, levels):
        serialized = []
        for price, orders in levels.items():
            serialized.append([
                str(price),
                [self._serialize_order(order) for order in orders]
            ])
        return serialized
    
    def _deserialize_levels(self, levels):
        deserialized = {}
        for price_level in levels:
            price = Decimal(price_level[0])
            orders = deque([self._deserialize_order(order) for order in price_level[1]])
            deserialized[price] = orders
        return deserialized
    
    def _serialize_order(self, order):
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "order_type": order.order_type,
            "side": order.side,
            "quantity": str(order.quantity),
            "price": str(order.price) if order.price else None,
            "stop_price": str(order.stop_price) if hasattr(order, 'stop_price') and order.stop_price else None,
            "take_profit_price": str(order.take_profit_price) if hasattr(order, 'take_profit_price') and order.take_profit_price else None,
            "timestamp": order.timestamp.isoformat()
        }
    
    def _deserialize_order(self, order_dict):
        from .models import Order, OrderType, OrderSide
        return Order(
            order_id=order_dict["order_id"],
            symbol=order_dict["symbol"],
            order_type=OrderType(order_dict["order_type"]),
            side=OrderSide(order_dict["side"]),
            quantity=Decimal(order_dict["quantity"]),
            price=Decimal(order_dict["price"]) if order_dict["price"] else None,
            stop_price=Decimal(order_dict["stop_price"]) if order_dict.get("stop_price") else None,
            take_profit_price=Decimal(order_dict["take_profit_price"]) if order_dict.get("take_profit_price") else None,
            timestamp=order_dict["timestamp"]
        ) 