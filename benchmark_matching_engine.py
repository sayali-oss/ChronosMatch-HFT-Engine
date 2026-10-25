
import random
import statistics
import time

from matching_engine import MatchingEngine


def generate_benchmark_orders(total_orders=10_000, seed=42):
    """Generate a repeatable workload for benchmark comparisons."""
    rng = random.Random(seed)
    orders = []

    for order_id in range(1, total_orders + 1):
        orders.append({
            "order_id": order_id,
            "side": rng.choice(["BUY", "SELL"]),
            "price": round(rng.uniform(100.00, 110.00), 2),
            "quantity": rng.randint(1, 1000),
            "timestamp": order_id,
        })

    return orders


def percentile(values, p):
    """Calculate a percentile using the nearest-rank method."""
    if not values:
        raise ValueError("Cannot calculate a percentile of empty data.")

    if not 0 < p <= 1:
        raise ValueError("Percentile p must be greater than 0 and at most 1.")

    ordered = sorted(values)
    index = max(0, int(len(ordered) * p + 0.999999) - 1)
    return ordered[index]


def run_single_benchmark(orders):
    """Measure one run using a pre-generated workload."""
    engine = MatchingEngine()
    latencies_ns = []

    start_total_ns = time.perf_counter_ns()

    for order in orders:
        start_ns = time.perf_counter_ns()
        engine.add_order(order)
        latencies_ns.append(time.perf_counter_ns() - start_ns)

    elapsed_ns = time.perf_counter_ns() - start_total_ns
    elapsed_seconds = elapsed_ns / 1_000_000_000
    latencies_us = [value / 1000 for value in latencies_ns]

    return {
        "elapsed_seconds": elapsed_seconds,
        "throughput": len(orders) / elapsed_seconds,
        "average_us": statistics.mean(latencies_us),
        "p50_us": percentile(latencies_us, 0.50),
        "p95_us": percentile(latencies_us, 0.95),
        "p99_us": percentile(latencies_us, 0.99),
        "max_us": max(latencies_us),
        "trades": len(engine.trades),
        "open_buy": len(engine.buy_orders),
        "open_sell": len(engine.sell_orders),
    }


def benchmark_matching_engine(
    total_orders=10_000,
    seed=42,
    repetitions=5,
):
    """Run repeated measurements over the same deterministic workload."""
    if total_orders <= 0:
        raise ValueError("total_orders must be positive.")

    if repetitions <= 0:
        raise ValueError("repetitions must be positive.")

    orders = generate_benchmark_orders(total_orders, seed)

    # Warm up Python and the engine before collecting measurements.
    warmup_orders = orders[:min(500, total_orders)]
    run_single_benchmark(warmup_orders)

    results = []

    for run_number in range(1, repetitions + 1):
        result = run_single_benchmark(orders)
        results.append(result)

        print(
            f"Run {run_number}/{repetitions}: "
            f"{result['throughput']:,.2f} orders/sec, "
            f"average latency {result['average_us']:.3f} us"
        )

    median_throughput = statistics.median(
        result["throughput"] for result in results
    )
    median_average_latency = statistics.median(
        result["average_us"] for result in results
    )

    # Use the final run for workload outcome counts.
    final = results[-1]

    print("\n===== MATCHING ENGINE BENCHMARK =====")
    print(f"Orders per run       : {total_orders:,}")
    print(f"Random seed          : {seed}")
    print(f"Repetitions          : {repetitions}")
    print(f"Median throughput    : {median_throughput:,.2f} orders/sec")
    print(f"Median average latency: {median_average_latency:.3f} us")
    print(f"Final-run elapsed    : {final['elapsed_seconds']:.4f} seconds")
    print(f"Final-run p50 latency: {final['p50_us']:.3f} us")
    print(f"Final-run p95 latency: {final['p95_us']:.3f} us")
    print(f"Final-run p99 latency: {final['p99_us']:.3f} us")
    print(f"Final-run max latency: {final['max_us']:.3f} us")
    print(f"Trades executed      : {final['trades']:,}")
    print(f"Open BUY orders      : {final['open_buy']:,}")
    print(f"Open SELL orders     : {final['open_sell']:,}")

    # All repetitions should process the same workload and produce
    # the same matching outcomes.
    outcomes = {
        (r["trades"], r["open_buy"], r["open_sell"])
        for r in results
    }

    if len(outcomes) != 1:
        raise AssertionError("Matching outcomes differed between runs.")

    print("Outcome consistency  : PASS")
    print("Result               : PASS")


if __name__ == "__main__":
    benchmark_matching_engine()
