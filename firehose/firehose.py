
import asyncio
import time
import sys
from pathlib import Path

# Add the project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from firehose.order_generator import generate_order
from mmap_ring_buffer import MMapRingBuffer


async def firehose(order_rate=1000, duration=5):
    """
    Generate trading orders and pass them through the mmap ring buffer.

    order_rate: Target order count per second (used to calculate total count).
    duration: Duration parameter used to calculate total order count.
    """

    total_orders = order_rate * duration

    # Create a 1 KB ring buffer.
    ring = MMapRingBuffer(size=1024)

    generated = 0
    consumed = 0

    print("\n========================================")
    print("       CHRONOSMATCH MARKET FIREHOSE")
    print("========================================")
    print(f"Target order count: {total_orders:,}")
    print(f"Record size       : {ring.msg_size} bytes")
    print("----------------------------------------")

    start_ns = time.perf_counter_ns()

    try:
        for order_id in range(1, total_orders + 1):
            order = generate_order(order_id)

            # Write the order into the ring buffer.
            # If full, consume one order and retry.
            while not ring.write_order(order):
                recovered = ring.read_order()

                if recovered is not None:
                    consumed += 1

            generated += 1

            # Give the asyncio event loop an opportunity to run.
            await asyncio.sleep(0)

            # Consume one order and verify its ID.
            recovered = ring.read_order()

            if recovered is not None:
                consumed += 1

                assert recovered["order_id"] == order["order_id"], (
                    f"Order ID mismatch: expected {order['order_id']}, "
                    f"got {recovered['order_id']}"
                )

        # Consume any remaining records.
        while True:
            recovered = ring.read_order()

            if recovered is None:
                break

            consumed += 1

        elapsed_seconds = (
            time.perf_counter_ns() - start_ns
        ) / 1_000_000_000

        print(f"Orders generated : {generated:,}")
        print(f"Orders consumed  : {consumed:,}")
        print(f"Time taken       : {elapsed_seconds:.6f} seconds")
        print(
            f"Throughput       : "
            f"{generated / elapsed_seconds:,.2f} orders/sec"
        )

        if generated != consumed:
            raise RuntimeError(
                f"Order count mismatch: generated={generated}, "
                f"consumed={consumed}"
            )

        print("Status           : PASS")
        print("========================================\n")

    finally:
        ring.close()


async def main():
    await firehose(order_rate=1000, duration=5)


if __name__ == "__main__":
    asyncio.run(main())
