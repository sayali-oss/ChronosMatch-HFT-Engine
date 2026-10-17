
import time
import statistics

from firehose.order_generator import generate_order
from mmap_ring_buffer import MMapRingBuffer


def benchmark_latency(total_orders=100_000):
    ring = MMapRingBuffer(size=1024 * 1024)
    latencies_ns = []

    try:
        for order_id in range(1, total_orders + 1):
            order = generate_order(order_id)

            start_ns = time.perf_counter_ns()

            written = ring.write_order(order)
            if not written:
                raise RuntimeError("Ring buffer unexpectedly full")

            recovered = ring.read_order()

            end_ns = time.perf_counter_ns()

            if recovered is None:
                raise RuntimeError("No order was recovered")

            if recovered["order_id"] != order_id:
                raise RuntimeError("Order ID mismatch")

            latencies_ns.append(end_ns - start_ns)

        latencies_us = [value / 1000 for value in latencies_ns]

        print("\n===== CHRONOSMATCH LATENCY BENCHMARK =====")
        print(f"Orders processed : {total_orders:,}")
        print(f"Average latency  : {statistics.mean(latencies_us):.3f} us")
        print(f"Median (p50)     : {statistics.median(latencies_us):.3f} us")
        print(f"p95 latency      : {sorted(latencies_us)[int(total_orders * 0.95) - 1]:.3f} us")
        print(f"p99 latency      : {sorted(latencies_us)[int(total_orders * 0.99) - 1]:.3f} us")
        print(f"Maximum latency  : {max(latencies_us):.3f} us")
        print("Result           : PASS")

    finally:
        ring.close()


if __name__ == "__main__":
    benchmark_latency()
