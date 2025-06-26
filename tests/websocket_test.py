import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Subscribe to BTC-USDT orderbook updates
        subscribe_message = {
            "type": "subscribe",
            "channel": "orderbook",
            "symbol": "BTC-USDT"
        }
        await websocket.send(json.dumps(subscribe_message))
        print(f"Sent subscription request: {json.dumps(subscribe_message, indent=2)}")
        
        # Keep connection open to receive messages
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received: {json.dumps(data, indent=2)}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

# Run the test
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_websocket()) 