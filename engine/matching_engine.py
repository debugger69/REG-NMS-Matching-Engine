from decimal import Decimal
from .models import Order, OrderType, OrderSide, Trade
from .order_book import OrderBook
from .account_manager import AccountManager
import logging
from collections import defaultdict

class MatchingEngine:
    def __init__(self, persistence_manager=None, fee_config=None, account_manager=None):
        self.order_books = defaultdict(lambda: OrderBook(""))  # symbol -> OrderBook
        self.logger = logging.getLogger(__name__)
        self.trade_listeners = []
        self.persistence_manager = persistence_manager
        self.last_trade_prices = {}  # Track last trade price per symbol
        self.fee_config = fee_config or {
            "maker_fee": Decimal("0.001"),  # 0.1%
            "taker_fee": Decimal("0.002"),  # 0.2%
            "fee_currency": "USDT"
        }
        self.account_manager = account_manager or AccountManager()
    
    def add_trade_listener(self, listener):
        self.trade_listeners.append(listener)
    
    def notify_trade(self, trade: Trade):
        """Update last trade price and notify listeners"""
        # Update last trade price
        self.last_trade_prices[trade.symbol] = trade.price
        
        # Notify listeners
        for listener in self.trade_listeners:
            listener(trade)
    
    def _get_last_trade_price(self, symbol: str) -> Decimal | None:
        """Get the last trade price for a symbol"""
        return self.last_trade_prices.get(symbol)
    
    def update_market_price(self, symbol: str, price: Decimal):
        """Explicitly update the market price for a symbol and trigger advanced orders if needed."""
        self.last_trade_prices[symbol] = price
        self._check_stop_orders(symbol)
    
    def process_order(self, order: Order, user_id: str = None, trigger_price: Decimal = None) -> list:
        symbol = order.symbol
        order_book = self.order_books[symbol]
        order_book.symbol = symbol  # Ensure symbol is set
        
        executions = []
        
        # Check sufficient funds for buy orders (if user_id provided)
        if user_id and order.side == OrderSide.BUY and order.order_type in [OrderType.LIMIT, OrderType.MARKET, OrderType.IOC, OrderType.FOK]:
            # For simplicity, assume quote currency is always USDT
            required = (order.price or 0) * order.quantity if order.price else order.quantity
            if not self.account_manager.has_sufficient_funds(user_id, "USDT", required):
                raise ValueError("Insufficient funds for order")
        
        # Matching logic
        if order.side == OrderSide.BUY:
            executions = self._match_buy_order(order, order_book)
        else:
            executions = self._match_sell_order(order, order_book)
        
        # Handle remaining quantity
        if order.quantity > 0:
            if order.order_type == OrderType.LIMIT:
                order_book.add_order(order)
            elif order.order_type in [OrderType.IOC, OrderType.FOK]:
                self.logger.info(f"{order.order_type} order partially filled, canceling remainder")
            elif order.order_type == OrderType.STOP_LOSS or order.order_type == OrderType.STOP_LIMIT:
                order_book.add_stop_order(order)
            elif order.order_type == OrderType.TAKE_PROFIT:
                order_book.add_take_profit_order(order)
        
        # After processing, check stop orders if we had trades
        if executions:
            self._check_stop_orders(symbol)
        
        if trigger_price is not None:
            self.update_market_price(symbol, trigger_price)
        
        return executions
    
    def _check_stop_orders(self, symbol: str):
        """Check and trigger stop and take-profit orders based on last trade price"""
        last_price = self._get_last_trade_price(symbol)
        if not last_price:
            return
        order_book = self.order_books.get(symbol)
        if not order_book:
            return
        # Process stop orders
        for stop_order in list(order_book.stop_orders):
            if (stop_order.side == OrderSide.BUY and stop_order.stop_price and last_price >= stop_order.stop_price):
                self._trigger_stop_order(stop_order)
                order_book.stop_orders.remove(stop_order)
            elif (stop_order.side == OrderSide.SELL and stop_order.stop_price and last_price <= stop_order.stop_price):
                self._trigger_stop_order(stop_order)
                order_book.stop_orders.remove(stop_order)
        # Process take-profit orders
        for tp_order in list(order_book.take_profit_orders):
            if (tp_order.side == OrderSide.BUY and tp_order.take_profit_price and last_price <= tp_order.take_profit_price):
                self._trigger_take_profit_order(tp_order)
                order_book.take_profit_orders.remove(tp_order)
            elif (tp_order.side == OrderSide.SELL and tp_order.take_profit_price and last_price >= tp_order.take_profit_price):
                self._trigger_take_profit_order(tp_order)
                order_book.take_profit_orders.remove(tp_order)

    def _trigger_stop_order(self, order: Order):
        """Convert stop/stop-limit order to market/limit order and process it"""
        if order.order_type == OrderType.STOP_LIMIT:
            limit_order = Order(
                order_id=f"{order.order_id}-triggered",
                symbol=order.symbol,
                order_type=OrderType.LIMIT,
                side=order.side,
                quantity=order.quantity,
                price=order.price
            )
            self.process_order(limit_order)
        else:
            market_order = Order(
                order_id=f"{order.order_id}-triggered",
                symbol=order.symbol,
                order_type=OrderType.MARKET,
                side=order.side,
                quantity=order.quantity
            )
            self.process_order(market_order)

    def _trigger_take_profit_order(self, order: Order):
        """Convert take-profit order to limit order and process it"""
        limit_order = Order(
            order_id=f"{order.order_id}-triggered",
            symbol=order.symbol,
            order_type=OrderType.LIMIT,
            side=order.side,
            quantity=order.quantity,
            price=order.price or order.take_profit_price
        )
        self.process_order(limit_order)
    
    def _match_buy_order(self, order: Order, order_book: OrderBook) -> list:
        executions = []
        total_available = 0
        # FOK: Check if enough quantity is available at or better than price
        if order.order_type == OrderType.FOK:
            needed = order.quantity
            qty = 0
            temp_qty = needed
            for price, orders in order_book.asks.items():
                if order.price is not None and price > order.price:
                    break
                for o in orders:
                    qty += o.quantity
                    if qty >= needed:
                        break
                if qty >= needed:
                    break
            if qty < needed:
                return []
        while order.quantity > 0 and order_book.asks:
            best_ask_price, best_ask_orders = order_book.asks.peekitem(0)
            if order.order_type == OrderType.LIMIT and order.price < best_ask_price:
                break
            if order.order_type == OrderType.FOK and order.price < best_ask_price:
                break
            best_ask_order = best_ask_orders[0]
            execution_price = best_ask_price
            execution_quantity = min(order.quantity, best_ask_order.quantity)
            trade = Trade(
                symbol=order.symbol,
                price=execution_price,
                quantity=execution_quantity,
                aggressor_side=order.side,
                maker_order_id=best_ask_order.order_id,
                taker_order_id=order.order_id,
                maker_fee=execution_quantity * execution_price * self.fee_config["maker_fee"],
                taker_fee=execution_quantity * execution_price * self.fee_config["taker_fee"],
                fee_currency=self.fee_config["fee_currency"]
            )
            executions.append(trade)
            self.notify_trade(trade)
            order.quantity -= execution_quantity
            best_ask_order.quantity -= execution_quantity
            if best_ask_order.quantity <= 0:
                best_ask_orders.popleft()
                if not best_ask_orders:
                    del order_book.asks[best_ask_price]
            if order.order_type == OrderType.FOK and order.quantity > 0:
                break
        return executions
    
    def _match_sell_order(self, order: Order, order_book: OrderBook) -> list:
        executions = []
        while order.quantity > 0 and order_book.bids:
            best_bid_price, best_bid_orders = order_book.bids.peekitem(0)
            
            if order.order_type == OrderType.LIMIT and order.price > best_bid_price:
                break
                
            best_bid_order = best_bid_orders[0]
            execution_price = best_bid_price
            execution_quantity = min(order.quantity, best_bid_order.quantity)
            
            trade = Trade(
                symbol=order.symbol,
                price=execution_price,
                quantity=execution_quantity,
                aggressor_side=order.side,
                maker_order_id=best_bid_order.order_id,
                taker_order_id=order.order_id,
                maker_fee=execution_quantity * execution_price * self.fee_config["maker_fee"],
                taker_fee=execution_quantity * execution_price * self.fee_config["taker_fee"],
                fee_currency=self.fee_config["fee_currency"]
            )
            executions.append(trade)
            self.notify_trade(trade)
            
            order.quantity -= execution_quantity
            best_bid_order.quantity -= execution_quantity
            
            if best_bid_order.quantity <= 0:
                best_bid_orders.popleft()
                if not best_bid_orders:
                    del order_book.bids[best_bid_price]
            
            if order.order_type == OrderType.FOK and order.quantity > 0:
                break
        
        return executions
    
    def shutdown(self):
        """Shutdown the matching engine and save state if persistence is enabled"""
        if self.persistence_manager:
            for symbol, order_book in self.order_books.items():
                self.persistence_manager.save_order_book(symbol, order_book)