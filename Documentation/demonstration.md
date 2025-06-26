# Matching Engine Demonstration Guide

## 1. System Functionality Demonstration

# Setup
1. Start the server:
```bash
python run.py
```

2. In a separate terminal, start the WebSocket client to observe real-time updates:
```bash
python tests/websocket_test.py
```

# A. Basic Order Flow Demonstration

1. Submit a limit sell order (Create a sell wall at 50,000):
```python
import requests
import json

def place_order(order_data):
    response = requests.post('http://localhost:8000/order', json=order_data)
    return json.loads(response.text)

# Place a large sell limit order
sell_limit_order = {
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "sell",
    "quantity": 10.0,
    "price": 50000.0
}
result = place_order(sell_limit_order)
print(f"Sell order result: {json.dumps(result, indent=2)}")

# Check the orderbook
orderbook = requests.get('http://localhost:8000/orderbook/BTC-USDT')
print(f"Orderbook after sell order: {json.dumps(orderbook.json(), indent=2)}")
```

2. Submit matching buy orders:
```python
# Place a smaller buy order at market price
buy_market_order = {
    "symbol": "BTC-USDT",
    "order_type": "market",
    "side": "buy",
    "quantity": 1.0
}
result = place_order(buy_market_order)
print(f"Market buy result: {json.dumps(result, indent=2)}")

# Place a limit buy order
buy_limit_order = {
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": 2.0,
    "price": 50000.0
}
result = place_order(buy_limit_order)
print(f"Limit buy result: {json.dumps(result, indent=2)}")
```

# B. Advanced Order Types Demonstration

1. Stop-Loss Order:
```python
stop_loss_order = {
    "symbol": "BTC-USDT",
    "order_type": "stop_loss",
    "side": "sell",
    "quantity": 1.0,
    "stop_price": 49000.0  # Triggers when price falls to this level
}
result = place_order(stop_loss_order)
print(f"Stop-loss order result: {json.dumps(result, indent=2)}")
```

2. Take-Profit Order:
```python
take_profit_order = {
    "symbol": "BTC-USDT",
    "order_type": "take_profit",
    "side": "sell",
    "quantity": 1.0,
    "take_profit_price": 51000.0  # Triggers when price rises to this level
}
result = place_order(take_profit_order)
print(f"Take-profit order result: {json.dumps(result, indent=2)}")
```

3. Fill-or-Kill (FOK) Order:
```python
fok_order = {
    "symbol": "BTC-USDT",
    "order_type": "fok",
    "side": "buy",
    "quantity": 5.0,
    "price": 50000.0
}
result = place_order(fok_order)
print(f"FOK order result: {json.dumps(result, indent=2)}")
```

## 2. Core Matching Logic and Data Structures

# Key Components

1. Order Book Structure (`engine/order_book.py`):

'''
from sortedcontainers import SortedDict

class OrderBook:
    def __init__(self, symbol):
        # Price-time priority using SortedDict for O(log n) operations
        self.bids = SortedDict()  # Higher prices first
        self.asks = SortedDict()  # Lower prices first
        self.symbol = symbol
 '''
# further code in order_book.py



2. Matching Engine Core (`engine/matching_engine.py`):
- Uses price-time priority
- Maintains separate order books per symbol
- Processes orders atomically
- Handles different order types through a strategy pattern

# Order Matching Process

1. Order Arrival:
   - New order validated
   - Routed to correct order book
   - Order type handler selected

2. Matching Process:
   - For market orders: Cross against opposite side immediately
   - For limit orders: Check for immediate crosses, then add to book
   - For stop orders: Add to trigger queue

3. Price-Time Priority:
   - Orders at better prices execute first
   - At same price, older orders execute first

## 3. Design Choices and REG NMS Implementation

# REG NMS-Inspired Features

1. Price-Time Priority:
   - Ensures fair execution
   - Rewards liquidity providers who quote first
   - Prevents queue jumping

2. Trade-Through Prevention:
   - Orders execute at best available prices
   - Market orders walk the book for best execution
   - Limit orders never cross the spread inappropriately

# Key Design Choices

1. Data Structures:
   - SortedDict for order books: O(log n) operations
   - Hash maps for order lookups: O(1) access
   - Priority queues for stop orders: Efficient trigger processing

2. Concurrency Model:
   - Single-threaded core for consistency
   - Async API layer for scalability
   - WebSocket for real-time updates

3. Order Type Implementation:
   - Strategy pattern for different order types
   - Pluggable architecture for new order types
   - Clear separation of concerns

# Performance Considerations

1. Memory Efficiency:
   - Compact order representation
   - Reference counting for shared data
   - Efficient price level aggregation

2. Processing Speed:
   - Optimized matching algorithm
   - Minimal object allocation
   - Efficient data structure choices

## Testing the Implementation

Run the following test suites to verify functionality:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_matching.py  # Core matching logic
python -m pytest tests/test_advanced_orders.py  # Advanced order types
python -m pytest tests/test_fees.py  # Fee calculation
.
.
.
.
```

## Benchmarking

Run the benchmark to measure performance:

```bash
# Via HTTP endpoint
curl http://localhost:8000/benchmark?num_orders=10000

# Or via Python script
python -m engine.benchmark
```
