
import time

from firehose.order_generator import generate_order
from mmap_ring_buffer import MMapRingBuffer


def benchmark(total_orders=100_000):
    ring = MMapRingBuffer(size=1024 * 1024)

    generated = 0
    consumed = 0
    start = time.perf_counter()

    try:
        for order_id in range(1, total_orders + 1):
            order = generate_order(order_id)

            # Keep writing until space is available.
            while not ring.write_order(order):
                if ring.read_order() is not None:
                    consumed += 1

            generated += 1

            recovered = ring.read_order()
            if recovered is not None:
                consumed += 1

                assert recovered["order_id"] == order_id, (
                    f"Expected order {order_id}, "
                    f"got {recovered['order_id']}"
                )

        # Drain any remaining orders.
        while ring.read_order() is not None:
            consumed += 1

        elapsed = time.perf_counter() - start
        throughput = generated / elapsed if elapsed > 0 else 0

        print("\n===== CHRONOSMATCH BENCHMARK =====")
        print(f"Orders generated : {generated:,}")
        print(f"Orders consumed  : {consumed:,}")
        print(f"Elapsed time     : {elapsed:.4f} seconds")
        print(f"Throughput       : {throughput:,.2f} orders/sec")
        print(f"Result           : {'PASS' if generated == consumed else 'FAIL'}")

    finally:
        ring.close()


if __name__ == "__main__":
    benchmark(total_orders=1_000_000)
