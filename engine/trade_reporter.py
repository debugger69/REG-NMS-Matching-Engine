from datetime import datetime

class TradeReport:
    def __init__(self, trade):
        self.timestamp = datetime.utcnow().isoformat()
        self.symbol = trade.symbol
        self.trade_id = trade.id
        self.price = trade.price
        self.quantity = trade.quantity
        self.aggressor_side = trade.taker_side
        self.maker_order_id = trade.maker_order_id
        self.taker_order_id = trade.taker_order_id