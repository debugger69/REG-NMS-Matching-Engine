# API Documentation (Detailed)

## REST API Endpoints

### POST /order
- **Description:** Submit a new order to the matching engine.
- **Request Body:**
  - `symbol` (str): Trading pair, e.g., "BTC-USDT".
  - `order_type` (str): One of "market", "limit", "ioc", "fok", "stop_loss", "stop_limit", "take_profit".
  - `side` (str): "buy" or "sell".
  - `quantity` (decimal): Order quantity (must be positive).
  - `price` (decimal, optional): Required for limit, stop-limit, and take-profit orders.
  - `stop_price` (decimal, optional): Required for stop-loss and stop-limit orders.
  - `take_profit_price` (decimal, optional): Required for take-profit orders.
- **Response:**
  - `status`: "success" or "error".
  - `executions`: List of trade execution details (see TradeResponse).
  - `error` (optional): Error message if the order was rejected.

### GET /orderbook/{symbol}
- **Description:** Retrieve the current order book depth for a given symbol.
- **Query Parameters:**
  - `depth` (int, optional): Number of price levels to return (default: 10).
- **Response:**
  - `bids`: List of [price, quantity] for top N bid levels.
  - `asks`: List of [price, quantity] for top N ask levels.

### GET /benchmark
- **Description:** Run a performance benchmark on the matching engine.
- **Query Parameters:**
  - `num_orders` (int, optional): Number of synthetic orders to process (default: 1000).
- **Response:**
  - `orders_per_second`: Throughput.
  - `total_time_seconds`: Total benchmark duration.
  - `latency_microseconds`: Min, max, mean, median, stdev per order.
  - `matches_per_order`: Min, max, mean, median, stdev.
  - `total_trades`: Number of trades executed.

## WebSocket API

### Connecting to WebSocket
To connect to the WebSocket API, you can use the provided Python client in `tests/websocket_test.py`. Here's how to use it:

1. Make sure your server is running:
   ```bash
   python -m uvicorn main:app --reload
   ```

2. Run the WebSocket test client:
   ```bash
   python tests/websocket_test.py
   ```

The client will automatically:
- Connect to the WebSocket endpoint at `ws://localhost:8000/ws`
- Subscribe to orderbook updates for BTC-USDT
- Print any received messages in a formatted JSON format

You can modify the subscription message in the test script to subscribe to different symbols or channels.

Example subscription message:
```json
{
    "type": "subscribe",
    "channel": "orderbook",
    "symbol": "BTC-USDT"
}
```

### Market Data Feed
- **Connect:** `ws://<host>:<port>/ws`
- **Message Type:** `market_data`
- **Payload:**
  - `timestamp` (ISO8601)
  - `symbol` (str)
  - `asks`: List of [price, quantity] (top N levels)
  - `bids`: List of [price, quantity] (top N levels)
- **Usage:** Subscribe to real-time order book and BBO updates for any symbol.

### Trade Execution Feed
- **Message Type:** `trade`
- **Payload:**
  - `timestamp` (ISO8601)
  - `symbol` (str)
  - `trade_id` (str)
  - `price` (decimal)
  - `quantity` (decimal)
  - `aggressor_side` ("buy"/"sell")
  - `maker_order_id` (str)
  - `taker_order_id` (str)
  - `maker_fee` (decimal)
  - `taker_fee` (decimal)
  - `fee_currency` (str)
- **Usage:** Subscribe to real-time trade execution reports for any symbol.

## Data Models

### OrderRequest
- `symbol` (str)
- `order_type` (str)
- `side` (str)
- `quantity` (decimal)
- `price` (decimal, optional)
- `stop_price` (decimal, optional)
- `take_profit_price` (decimal, optional)

### MarketDataResponse
- `timestamp` (str)
- `symbol` (str)
- `asks` (list)
- `bids` (list)

### TradeResponse
- `timestamp` (str)
- `symbol` (str)
- `trade_id` (str)
- `price` (decimal)
- `quantity` (decimal)
- `aggressor_side` (str)
- `maker_order_id` (str)
- `taker_order_id` (str)
- `maker_fee` (decimal)
- `taker_fee` (decimal)
- `fee_currency` (str)

## Error Handling
- All endpoints return clear error messages for invalid parameters, insufficient funds, or internal errors.
- HTTP status codes are used appropriately (400 for bad request, 404 for not found, etc.).
- WebSocket errors are logged and connections are cleaned up.

## Authentication & Security (if applicable)
- (Add here if you implement authentication, rate limiting, or other security features.)

---
For further details, see code comments, docstrings, and the OpenAPI schema at `/docs`.
