from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse
from api import rest_api, websocket_api
from engine.matching_engine import MatchingEngine
from engine.persistence import PersistenceManager
from engine.order_book import OrderBook  # Add this import
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()
persistence = PersistenceManager()
engine = MatchingEngine(persistence_manager=persistence)
ws_manager = websocket_api.WebSocketManager(engine)

# Include routers
app.include_router(rest_api.router)  # Changed from rest_api.app to rest_api.router

@app.on_event("startup")
async def startup_event():
    logging.info("Starting matching engine")
    # REMOVE: await engine.start_processing()  <-- This line is causing the error
    
    # Load saved state
    logging.info("Loading saved order books...")
    for symbol in ["BTC-USDT"]:
        saved_state = persistence.load_order_book(symbol)
        if saved_state:
            order_book = OrderBook(symbol)
            order_book.bids = saved_state["bids"]
            order_book.asks = saved_state["asks"]
            engine.order_books[symbol] = order_book
    logging.info("Matching engine started")

@app.on_event("shutdown")
def shutdown_event():
    logging.info("Shutting down matching engine")
    engine.shutdown()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
    finally:
        ws_manager.disconnect(websocket)

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)