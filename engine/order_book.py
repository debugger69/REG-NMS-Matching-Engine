from sortedcontainers import SortedDict
from collections import deque
from decimal import Decimal
from .models import Order, OrderSide
import logging

class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids = SortedDict(lambda x: -x)  # Descending prices
        self.asks = SortedDict()  # Ascending prices
        self.stop_orders = []  # Stop-loss and stop-limit orders
        self.take_profit_orders = []  # Take-profit orders
        self.logger = logging.getLogger(__name__)
        self.order_map = {}  # order_id -> (price, index in queue)
    
    def add_order(self, order: Order):
        book = self.bids if order.side == OrderSide.BUY else self.asks
        price = order.price
        
        if price not in book:
            book[price] = deque()
        book[price].append(order)
        self.logger.debug(f"Added order {order.order_id} to {order.side} book at {price}")
        self.order_map[order.order_id] = (price, len(book[price])-1)
    
    def add_stop_order(self, order: Order):
        self.stop_orders.append(order)
        self.stop_orders.sort(key=lambda o: o.stop_price, 
                             reverse=(order.side == OrderSide.SELL))
        self.logger.debug(f"Added stop order {order.order_id} at {order.stop_price}")
    
    def add_take_profit_order(self, order: Order):
        self.take_profit_orders.append(order)
        self.take_profit_orders.sort(key=lambda o: o.take_profit_price, 
                                    reverse=(order.side == OrderSide.BUY))
        self.logger.debug(f"Added take-profit order {order.order_id} at {order.take_profit_price}")
    
    def remove_order(self, price: Decimal, order_id: str, side: OrderSide):
        book = self.bids if side == OrderSide.BUY else self.asks
        if price in book:
            orders = book[price]
            for i, order in enumerate(orders):
                if order.order_id == order_id:
                    del orders[i]
                    self.logger.debug(f"Removed order {order_id} from {side} book at {price}")
                    if not orders:
                        del book[price]
                    return True
        return False
    
    @property
    def best_bid(self) -> Decimal | None:
        return self.bids.peekitem(0)[0] if self.bids else None
    
    @property
    def best_ask(self) -> Decimal | None:
        return self.asks.peekitem(0)[0] if self.asks else None
    
    def get_depth(self, levels: int = 10) -> dict:
        return {
            "bids": [(str(price), str(sum(o.quantity for o in orders))) 
                     for price, orders in list(self.bids.items())[:levels]],
            "asks": [(str(price), str(sum(o.quantity for o in orders))) 
                     for price, orders in list(self.asks.items())[:levels]]
        }