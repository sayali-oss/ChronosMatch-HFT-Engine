
import random
import tracemalloc

from matching_engine import MatchingEngine


def generate_workload(count=50_000, seed=42):
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


def profile_memory():
    orders = generate_workload()
    engine = MatchingEngine()

    tracemalloc.start()

    for order in orders:
        engine.add_order(order)

    snapshot = tracemalloc.take_snapshot()
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\n===== MEMORY ALLOCATION PROFILE =====")
    print(f"Orders processed: {len(orders):,}")
    print(f"Trades retained:  {len(engine.trades):,}")
    print(f"Order IDs stored: {len(engine.order_ids):,}")
    print(f"Open BUY orders:  {len(engine.buy_orders):,}")
    print(f"Open SELL orders: {len(engine.sell_orders):,}")
    print(f"Current memory:   {current_bytes / (1024 ** 2):.2f} MiB")
    print(f"Peak memory:      {peak_bytes / (1024 ** 2):.2f} MiB")

    print("\n===== TOP 15 ALLOCATION LOCATIONS =====")

    for stat in snapshot.statistics("lineno")[:15]:
        print(f"{stat.size / 1024:9.2f} KiB | "
              f"{stat.count:7,} blocks | {stat}")

    print("\nProfiling complete.")


if __name__ == "__main__":
    profile_memory()

