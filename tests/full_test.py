import requests
import json
import time
import subprocess
import os

BASE_URL = "http://localhost:8000"

def print_response(response):
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_order_book():
    print("TESTING ORDER BOOK MANAGEMENT")
    
    # Clear order book first
    response = requests.get(f"{BASE_URL}/orderbook/BTC-USDT")
    print("Initial order book:")
    print_response(response)
    
    # Submit buy order
    buy_order = {
        "symbol": "BTC-USDT",
        "order_type": "limit",
        "side": "buy",
        "quantity": 1.0,
        "price": 50000.0
    }
    response = requests.post(f"{BASE_URL}/order", json=buy_order)
    print("Buy order response:")
    print_response(response)
    
    # Check order book
    response = requests.get(f"{BASE_URL}/orderbook/BTC-USDT")
    print("Order book after buy:")
    print_response(response)
    
    # Submit matching sell order
    sell_order = {
        "symbol": "BTC-USDT",
        "order_type": "limit",
        "side": "sell",
        "quantity": 1.0,
        "price": 50000.0
    }
    response = requests.post(f"{BASE_URL}/order", json=sell_order)
    print("Sell order response:")
    print_response(response)
    
    # Check order book again
    response = requests.get(f"{BASE_URL}/orderbook/BTC-USDT")
    print("Order book after match:")
    print_response(response)

def test_advanced_orders():
    print("TESTING ADVANCED ORDER TYPES")
    
    # Test IOC order
    # First add a sell order
    sell_order = {
        "symbol": "ETH-USDT",
        "order_type": "limit",
        "side": "sell",
        "quantity": 0.5,
        "price": 3000.0
    }
    requests.post(f"{BASE_URL}/order", json=sell_order)
    
    # Submit IOC buy order for more quantity
    ioc_order = {
        "symbol": "ETH-USDT",
        "order_type": "ioc",
        "side": "buy",
        "quantity": 1.0,
        "price": 3000.0
    }
    response = requests.post(f"{BASE_URL}/order", json=ioc_order)
    print("IOC order response:")
    print_response(response)
    
    # Check order book
    response = requests.get(f"{BASE_URL}/orderbook/ETH-USDT")
    print("Order book after IOC:")
    print_response(response)

def test_stop_orders():
    print("TESTING STOP ORDERS")
    
    # Submit stop-loss order
    stop_order = {
        "symbol": "BTC-USDT",
        "order_type": "stop_loss",
        "side": "sell",
        "quantity": 1.0,
        "stop_price": 49000.0
    }
    response = requests.post(f"{BASE_URL}/order", json=stop_order)
    print("Stop order response:")
    print_response(response)
    
    # Create a trade below stop price
    buy_order = {
        "symbol": "BTC-USDT",
        "order_type": "limit",
        "side": "buy",
        "quantity": 0.1,
        "price": 48000.0
    }
    requests.post(f"{BASE_URL}/order", json=buy_order)
    
    sell_order = {
        "symbol": "BTC-USDT",
        "order_type": "limit",
        "side": "sell",
        "quantity": 0.1,
        "price": 48000.0
    }
    requests.post(f"{BASE_URL}/order", json=sell_order)
    
    # Check if stop order was triggered
    time.sleep(1)  # Give time for stop order processing
    response = requests.get(f"{BASE_URL}/orderbook/BTC-USDT")
    print("Order book after stop trigger:")
    print_response(response)

def test_persistence():
    print("TESTING PERSISTENCE")
    
    # Submit orders
    buy_order = {
        "symbol": "BTC-USDT",
        "order_type": "limit",
        "side": "buy",
        "quantity": 1.0,
        "price": 49000.0
    }
    requests.post(f"{BASE_URL}/order", json=buy_order)
    
    sell_order = {
        "symbol": "BTC-USDT",
        "order_type": "limit",
        "side": "sell",
        "quantity": 2.0,
        "price": 51000.0
    }
    requests.post(f"{BASE_URL}/order", json=sell_order)
    
    # Check order book before restart
    response = requests.get(f"{BASE_URL}/orderbook/BTC-USDT")
    print("Order book before restart:")
    print_response(response)
    
    print("Stopping server...")
    print("Check data/BTC-USDT_orderbook.json and restart the server manually")
    print("Then run the next test function")

def test_after_restart():
    print("TESTING AFTER RESTART")
    
    # Check order book after restart
    response = requests.get(f"{BASE_URL}/orderbook/BTC-USDT")
    print("Order book after restart:")
    print_response(response)

def test_performance():
    print("TESTING PERFORMANCE")
    
    # Run benchmark
    response = requests.get(f"{BASE_URL}/benchmark?num_orders=1000")
    print("Benchmark results:")
    print_response(response)

if __name__ == "__main__":
    test_order_book()
    test_advanced_orders()
    test_stop_orders()
    test_performance()
    test_persistence()
    # test_after_restart() # Run this after manually restarting the server
