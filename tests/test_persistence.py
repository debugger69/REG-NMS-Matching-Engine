from engine.persistence import PersistenceManager
from engine.order_book import OrderBook

def test_order_book_persistence():
    pm = PersistenceManager()
    order_book = OrderBook("BTC-USDT")
    # Add orders to order book
    pm.save_order_book("BTC-USDT", order_book)
    loaded = pm.load_order_book("BTC-USDT")
    assert loaded["bids"] == order_book.bids
    assert loaded["asks"] == order_book.asks 