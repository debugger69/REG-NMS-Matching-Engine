from fastapi import APIRouter, HTTPException
from engine.matching_engine import MatchingEngine
from engine.models import Order
from engine.benchmark import Benchmark
from .schemas import OrderRequest
import logging

router = APIRouter()
engine = MatchingEngine()
logger = logging.getLogger(__name__)

@router.post("/order")
async def submit_order(order_req: OrderRequest):
    """
    Submit a new order.
    Request body: {
        symbol: str,
        order_type: str (market, limit, ioc, fok, stop_loss, stop_limit, take_profit),
        side: str (buy/sell),
        quantity: decimal,
        price: decimal (optional)
    }
    Response: {status, executions}
    """
    try:
        order = Order(
            symbol=order_req.symbol,
            order_type=order_req.order_type,
            side=order_req.side,
            quantity=order_req.quantity,
            price=order_req.price
        )
        executions = engine.process_order(order)
        return {"status": "success", "executions": executions}
    except Exception as e:
        logger.error(f"Order processing failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, depth: int = 10):
    """
    Get current order book depth for a symbol.
    Query params: depth (default 10)
    Response: {bids, asks}
    """
    try:
        order_book = engine.order_books.get(symbol)
        if not order_book:
            return {"bids": [], "asks": []}
        return order_book.get_depth(depth)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/benchmark")
async def run_benchmark(num_orders: int = 1000):
    """
    Run a performance benchmark with the specified number of orders.
    Query params: num_orders
    Response: benchmark results
    """
    """Run a performance benchmark with the specified number of orders"""
    benchmark = Benchmark(engine)
    results = benchmark.measure_performance(num_orders)
    return results