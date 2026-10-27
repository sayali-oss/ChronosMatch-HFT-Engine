
import random
import time
import tracemalloc

from matching_engine import MatchingEngine


def generate_workload(count=50_000, seed=42):
    """Pre-generate orders so workload creation is excluded from memory measurements."""
    rng = random.Random(seed)
    orders = []

    for order_id in range(1, count + 1):
        orders.append({
            "order_id": order_id,
            "side": rng.choice(("BUY", "SELL")),
            "price": round(rng.uniform(100.0, 110.0), 2),
            "quantity": rng.randint(1, 1000),
            "timestamp": order_id,
        })

    return orders


def measure_memory():
    orders = generate_workload()

    engine = MatchingEngine()
    tracemalloc.start()

    start_time = time.perf_counter()

    for order in orders:
        engine.add_order(order)

    elapsed = time.perf_counter() - start_time
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\n===== MATCHING ENGINE MEMORY BASELINE =====")
    print(f"Orders processed       : {len(orders):,}")
    print(f"Trades executed        : {len(engine.trades):,}")
    print(f"Open BUY orders        : {len(engine.buy_orders):,}")
    print(f"Open SELL orders       : {len(engine.sell_orders):,}")
    print(f"Elapsed time           : {elapsed:.4f} seconds")
    print(f"Throughput             : {len(orders) / elapsed:,.2f} orders/sec")
    print(f"Current traced memory  : {current_bytes / (1024 ** 2):.2f} MiB")
    print(f"Peak traced memory     : {peak_bytes / (1024 ** 2):.2f} MiB")
    print(f"Memory per input order : {current_bytes / len(orders):.2f} bytes")
    print("Result                 : BASELINE RECORDED")


if __name__ == "__main__":
    measure_memory()
