
from mmap_ring_buffer import MMapRingBuffer
from matching_engine import MatchingEngine


def test_order_flows_from_ring_buffer_to_matching_engine():
    ring = MMapRingBuffer(size=1024)
    engine = MatchingEngine()

    orders = [
        {
            "order_id": 1,
            "side": "SELL",
            "price": 100.0,
            "quantity": 10,
            "timestamp": 1,
        },
        {
            "order_id": 2,
            "side": "BUY",
            "price": 101.0,
            "quantity": 4,
            "timestamp": 2,
        },
    ]

    try:
        # Write both orders into the ring buffer.
        for order in orders:
            assert ring.write_order(order)

        # Read them back in FIFO order and process them.
        while True:
            order = ring.read_order()
            if order is None:
                break
            engine.add_order(order)

        # Verify the complete order-processing flow.
        assert len(engine.trades) == 1
        assert engine.trades[0]["buy_order_id"] == 2
        assert engine.trades[0]["sell_order_id"] == 1
        assert engine.trades[0]["price"] == 100.0
        assert engine.trades[0]["quantity"] == 4

        # Six units of the original sell order remain.
        assert engine.sell_orders[0]["remaining"] == 6

    finally:
        ring.close()
