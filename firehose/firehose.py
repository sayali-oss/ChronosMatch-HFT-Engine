
import asyncio
import time
import sys
from pathlib import Path

# Add the project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from firehose.order_generator import generate_order
from mmap_ring_buffer import MMapRingBuffer
from matching_engine import MatchingEngine


async def firehose(order_rate=1000, duration=5):
    """
    Generate orders, transfer them through the ring buffer,
    and process them using the limit order matching engine.
    """

    total_orders = order_rate * duration
    ring = MMapRingBuffer(size=1024)
    engine = MatchingEngine()

    generated = 0
    consumed = 0
    expected_order_id = 1

    def process_order(order):
        nonlocal consumed, expected_order_id

        if order is None:
            return

        # Verify FIFO order from the ring buffer.
        assert order["order_id"] == expected_order_id, (
            f"Expected order {expected_order_id}, "
            f"got {order['order_id']}"
        )

        expected_order_id += 1
        consumed += 1

        # Send the recovered order to the matching engine.
        engine.add_order(order)

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

            # Write the order; free one slot and retry if full.
            while not ring.write_order(order):
                process_order(ring.read_order())

            generated += 1

            # Allow the asyncio event loop to run.
            await asyncio.sleep(0)

            # Consume and match one order.
            process_order(ring.read_order())

        # Drain any remaining orders.
        while True:
            recovered = ring.read_order()

            if recovered is None:
                break

            process_order(recovered)

        elapsed_seconds = (
            time.perf_counter_ns() - start_ns
        ) / 1_000_000_000

        open_buy = len(engine.buy_orders)
        open_sell = len(engine.sell_orders)

        print(f"Orders generated : {generated:,}")
        print(f"Orders consumed  : {consumed:,}")
        print(f"Trades executed  : {len(engine.trades):,}")
        print(f"Open BUY orders  : {open_buy:,}")
        print(f"Open SELL orders : {open_sell:,}")
        print(f"Time taken       : {elapsed_seconds:.6f} seconds")
        print(
            f"Throughput       : "
            f"{generated / elapsed_seconds:,.2f} orders/sec"
        )

        if generated != total_orders or consumed != total_orders:
            raise RuntimeError(
                f"Order count mismatch: generated={generated}, "
                f"consumed={consumed}, expected={total_orders}"
            )

        print("Status           : PASS")
        print("========================================\n")

    finally:
        ring.close()


async def main():
    await firehose(order_rate=1000, duration=5)


if __name__ == "__main__":
    asyncio.run(main())
