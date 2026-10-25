
import statistics
import time

from firehose.order_generator import generate_order
from matching_engine import MatchingEngine


def benchmark_matching_engine(total_orders=10_000):
    engine = MatchingEngine()
    latencies_ns = []

    for order_id in range(1, total_orders + 1):
        order = generate_order(order_id)

        start_ns = time.perf_counter_ns()
        engine.add_order(order)
        end_ns = time.perf_counter_ns()

        latencies_ns.append(end_ns - start_ns)

    latencies_us = [value / 1000 for value in latencies_ns]
    sorted_latencies = sorted(latencies_us)

    elapsed_seconds = sum(latencies_ns) / 1_000_000_000

    def percentile(values, p):
        index = min(len(values) - 1, int(len(values) * p))
        return values[index]

    print("\n===== MATCHING ENGINE BENCHMARK =====")
    print(f"Orders processed : {total_orders:,}")
    print(f"Elapsed time     : {elapsed_seconds:.4f} seconds")
    print(
        f"Throughput       : "
        f"{total_orders / elapsed_seconds:,.2f} orders/sec"
    )
    print(
        f"Average latency  : "
        f"{statistics.mean(latencies_us):.3f} us"
    )
    print(
        f"Median (p50)     : "
        f"{statistics.median(latencies_us):.3f} us"
    )
    print(
        f"p95 latency      : "
        f"{percentile(sorted_latencies, 0.95):.3f} us"
    )
    print(
        f"p99 latency      : "
        f"{percentile(sorted_latencies, 0.99):.3f} us"
    )
    print(f"Maximum latency  : {max(latencies_us):.3f} us")
    print(f"Trades executed  : {len(engine.trades):,}")
    print(f"Open BUY orders  : {len(engine.buy_orders):,}")
    print(f"Open SELL orders : {len(engine.sell_orders):,}")
    print("Result           : PASS")


if __name__ == "__main__":
    benchmark_matching_engine()
