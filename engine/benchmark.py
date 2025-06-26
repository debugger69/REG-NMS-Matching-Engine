import time
from decimal import Decimal
from engine.models import Order, OrderType, OrderSide
import statistics

class Benchmark:
    def __init__(self, engine):
        self.engine = engine
    
    def measure_performance(self, num_orders=1000):
        latencies = []
        match_counts = []
        trade_counts = []
        total_trades = 0
        start = time.perf_counter()
        
        for i in range(num_orders):
            order = Order(
                symbol="BTC-USDT",
                order_type=OrderType.LIMIT,
                side=OrderSide.BUY if i % 2 == 0 else OrderSide.SELL,
                quantity=Decimal("1.0"),
                price=Decimal(f"{50000 + (i % 100) + (0 if i % 2 == 0 else 200)}")
            )
            t0 = time.perf_counter()
            executions = self.engine.process_order(order)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1e6)  # microseconds
            match_counts.append(len(executions))
            total_trades += len(executions)
            trade_counts.append(total_trades)
        total_time = time.perf_counter() - start
        return {
            "orders_per_second": num_orders / total_time,
            "total_time_seconds": total_time,
            "num_orders_processed": num_orders,
            "latency_microseconds": {
                "min": min(latencies),
                "max": max(latencies),
                "mean": statistics.mean(latencies),
                "median": statistics.median(latencies),
                "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            "matches_per_order": {
                "min": min(match_counts),
                "max": max(match_counts),
                "mean": statistics.mean(match_counts),
                "median": statistics.median(match_counts),
                "stdev": statistics.stdev(match_counts) if len(match_counts) > 1 else 0
            },
            "total_trades": total_trades
        }

if __name__ == "__main__":
    from engine.matching_engine import MatchingEngine
    import json
    engine = MatchingEngine()
    bench = Benchmark(engine)
    results = bench.measure_performance(12000)
    print(json.dumps(results, indent=2))