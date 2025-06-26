from fastapi import WebSocket
import asyncio
import json
from engine.matching_engine import MatchingEngine
from engine.models import Trade
from .schemas import MarketDataResponse, TradeResponse
import logging
from datetime import datetime

class WebSocketManager:
    """
    WebSocket manager for market data and trade execution feeds.
    - Market data: type='market_data', data={timestamp, symbol, asks, bids}
    - Trade execution: type='trade', data={timestamp, symbol, trade_id, price, quantity, aggressor_side, maker_order_id, taker_order_id}
    """

    def __init__(self, engine: MatchingEngine):
        self.connections = set()
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        engine.add_trade_listener(self.notify_trade)
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"WebSocket send error: {str(e)}")
                self.disconnect(connection)
    
    async def notify_trade(self, trade: Trade):
        trade_resp = TradeResponse(
            timestamp=trade.timestamp.isoformat(),
            symbol=trade.symbol,
            trade_id=trade.trade_id,
            price=trade.price,
            quantity=trade.quantity,
            aggressor_side=trade.aggressor_side,
            maker_order_id=trade.maker_order_id,
            taker_order_id=trade.taker_order_id
        )
        await self.broadcast({
            "type": "trade",
            "data": trade_resp.dict()
        })
    
    async def broadcast_market_data(self, symbol: str):
        order_book = self.engine.order_books.get(symbol)
        if order_book:
            market_data = MarketDataResponse(
                timestamp=datetime.utcnow().isoformat(),
                symbol=symbol,
                asks=order_book.get_depth()["asks"],
                bids=order_book.get_depth()["bids"]
            )
            await self.broadcast({
                "type": "market_data",
                "data": market_data.dict()
            })