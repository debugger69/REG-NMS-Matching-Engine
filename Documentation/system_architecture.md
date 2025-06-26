# System Architecture and Design Documentation (Detailed)

## 1. System Architecture and Design Choices

The project is architected as a modular, extensible, and high-performance cryptocurrency matching engine, inspired by real-world exchange systems and regulatory principles (e.g., REG NMS). The main components are:

- **Engine Layer (`engine/`)**: Implements the core matching logic, order book management, advanced order types, persistence, benchmarking, and account management.
- **API Layer (`api/`)**: Exposes REST and WebSocket APIs for order submission, market data dissemination, and trade execution feeds. Built with FastAPI for async support and automatic documentation.
- **Testing Layer (`tests/`)**: Contains comprehensive unit and integration tests for all core and advanced features, including negative and edge cases.
- **Utilities (`utils/`)**: Provides centralized logging and error handling setup for diagnostics and audit trails.

**Design Choices:**
- **Python** was chosen for rapid development, readability, and strong ecosystem support. Performance-critical paths are optimized, and the design allows for future migration to C++ or Cython if needed.
- **FastAPI** is used for its async capabilities, speed, and built-in OpenAPI/Swagger documentation.
- **Modularity**: Each component (matching, order book, API, persistence) is decoupled for maintainability and extensibility.
- **Extensibility**: The system is designed to easily support new order types, symbols, and features.

---

## 2. Data Structures Used for the Order Book and Their Rationale

- **Order Book**:
  - Implemented using `SortedDict` (from `sortedcontainers`) for both bids and asks.
    - **Bids**: Sorted in descending order (highest price first).
    - **Asks**: Sorted in ascending order (lowest price first).
  - Each price level contains a `deque` (double-ended queue) of orders, ensuring FIFO (first-in, first-out) at each price level.
  - **Stop-loss, stop-limit, and take-profit orders** are managed in separate lists, sorted by trigger price.

**Rationale:**
- `SortedDict` provides O(log n) insertion, deletion, and access to best bid/ask, which is essential for real-time BBO (Best Bid and Offer) updates and efficient matching.
- `deque` ensures efficient FIFO order matching at each price, enforcing price-time priority.
- Separate lists for advanced order types allow for efficient triggering and management.

---

## 3. Matching Algorithm Implementation Details

- **Price-Time Priority**: Orders are matched strictly by price (better price first), then by time (earlier orders at the same price are filled first).
- **Order Matching**:
  - Incoming marketable orders (market, aggressive limit, IOC, FOK) are matched against the best available prices on the opposite side of the book.
  - The engine prevents "trade-throughs": no order is matched at a worse price than the current BBO.
  - Partial fills are supported; remaining quantity is handled according to order type (rest, cancel, or kill).
- **Advanced Order Types**:
  - **IOC**: Executes as much as possible immediately, cancels the rest.
  - **FOK**: Executes only if the entire quantity can be filled immediately; otherwise, cancels the order.
  - **Stop-Loss/Stop-Limit**: Triggered when the market price crosses the stop price, then submitted as a market or limit order.
  - **Take-Profit**: Triggered when the market price reaches the take-profit price, then submitted as a limit order.
- **Trade Reporting**: Each match generates a trade report, including price, quantity, maker/taker IDs, and fees. Trades are broadcast to clients in real time.
- **Account Management**: User balances are checked before order acceptance to ensure sufficient funds.

---

## 4. API Specifications (Detailed)

### REST API
- **POST `/order`**: Submit a new order.
  - Request: `{ symbol, order_type, side, quantity, price (optional) }`
  - Response: `{ status, executions (list of trade details) }`
- **GET `/orderbook/{symbol}`**: Get current order book depth for a symbol.
  - Query: `depth` (default 10)
  - Response: `{ bids, asks }` (top N levels)
- **GET `/benchmark`**: Run a performance benchmark.
  - Query: `num_orders` (default 1000)
  - Response: Benchmark results (orders/sec, latency, etc.)

### WebSocket API
- **Market Data Feed**: Real-time BBO and order book depth updates.
  - Message: `{ type: "market_data", data: { timestamp, symbol, asks, bids } }`
- **Trade Execution Feed**: Real-time trade execution reports.
  - Message: `{ type: "trade", data: { timestamp, symbol, trade_id, price, quantity, aggressor_side, maker_order_id, taker_order_id } }`

### Data Models
- **OrderRequest**: `{ symbol, order_type, side, quantity, price }`
- **MarketDataResponse**: `{ timestamp, symbol, asks, bids }`
- **TradeResponse**: `{ timestamp, symbol, trade_id, price, quantity, aggressor_side, maker_order_id, taker_order_id }`

---

## 5. Trade-off Decisions Made During Development

- **Language Choice**: Python was chosen for speed of development and clarity, with the understanding that C++ or Cython could be used for further optimization if needed.
- **Data Structures**: `SortedDict` and `deque` were selected for their balance of speed, clarity, and suitability for order book operations.
- **Extensibility vs. Simplicity**: The system is designed to be easily extensible for new order types and features, at the cost of some additional complexity.
- **Persistence**: Persistence is optional and modular, allowing for stateless or stateful deployments depending on operational needs.
- **API Design**: FastAPI was chosen for its async support, speed, and automatic OpenAPI documentation, making integration and client development easier.
- **Advanced Order Types**: Implemented as first-class citizens, but with explicit price feed/trigger logic for realistic and robust behavior.
- **Testing**: Comprehensive test coverage was prioritized to ensure reliability and maintainability.

---

## 6. How to Run Benchmark Testing

You can benchmark the matching engine's performance using the built-in benchmarking tool. This measures order processing throughput and latency.

### Step-by-Step Instructions

**Option 1: Run as a module (recommended)**
1. Open a terminal in your project root directory.
2. Run:
   ```
   python -m engine.benchmark
   ```
   This will print benchmark results (orders/sec, latency, etc.) to the terminal.

**Option 2: Run the script directly**
1. Open a terminal in your project root directory.
2. Run:
   ```
   python engine/benchmark.py
   ```
   If you see a `ModuleNotFoundError`, ensure your `PYTHONPATH` includes the project root, or use Option 1.

**Customizing the Benchmark**
- To change the number of orders, edit the `measure_performance` call in the `__main__` block of `engine/benchmark.py`.
- Example:
   ```python
   results = bench.measure_performance(5000)
   ```

**Output**
- The script prints a JSON report with throughput, latency stats, and trade counts.

---

For further details, see code comments, docstrings, and the API documentation in `docs/api_documentation.md`.
