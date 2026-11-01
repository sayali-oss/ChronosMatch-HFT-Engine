
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
        for order in orders:
            assert ring.write_order(order)

        while True:
            order = ring.read_order()
            if order is None:
                break
            engine.add_order(order)

        assert len(engine.trades) == 1
        assert engine.trades[0] == {
            "buy_order_id": 2,
            "sell_order_id": 1,
            "price": 100.0,
            "quantity": 4,
        }
        assert engine.sell_orders[0]["remaining"] == 6
    finally:
        ring.close()


def test_multiple_orders_flow_through_buffer_in_fifo_order():
    ring = MMapRingBuffer(size=1024)
    engine = MatchingEngine()

    orders = [
        {
            "order_id": 1,
            "side": "SELL",
            "price": 100.0,
            "quantity": 5,
            "timestamp": 1,
        },
        {
            "order_id": 2,
            "side": "SELL",
            "price": 101.0,
            "quantity": 3,
            "timestamp": 2,
        },
        {
            "order_id": 3,
            "side": "BUY",
            "price": 102.0,
            "quantity": 6,
            "timestamp": 3,
        },
    ]

    try:
        for order in orders:
            assert ring.write_order(order)

        recovered_ids = []

        while True:
            order = ring.read_order()
            if order is None:
                break

            recovered_ids.append(order["order_id"])
            engine.add_order(order)

        assert recovered_ids == [1, 2, 3]

        assert engine.trades == [
            {
                "buy_order_id": 3,
                "sell_order_id": 1,
                "price": 100.0,
                "quantity": 5,
            },
            {
                "buy_order_id": 3,
                "sell_order_id": 2,
                "price": 101.0,
                "quantity": 1,
            },
        ]

        assert len(engine.sell_orders) == 1
        assert engine.sell_orders[0]["order_id"] == 2
        assert engine.sell_orders[0]["remaining"] == 2

    finally:
        ring.close()


def test_ring_buffer_full_and_wraparound_preserve_order_flow():
    ring = MMapRingBuffer(size=128)
    engine = MatchingEngine()

    def make_order(order_id):
        return {
            "order_id": order_id,
            "side": "BUY",
            "price": 100.0 + order_id,
            "quantity": 1,
            "timestamp": order_id,
        }

    try:
        assert ring.write_order(make_order(1))
        assert ring.write_order(make_order(2))
        assert ring.write_order(make_order(3))
        assert not ring.write_order(make_order(4))

        first = ring.read_order()
        second = ring.read_order()

        assert first["order_id"] == 1
        assert second["order_id"] == 2

        assert ring.write_order(make_order(4))
        assert ring.write_order(make_order(5))
        assert not ring.write_order(make_order(6))

        recovered_ids = []

        while True:
            order = ring.read_order()
            if order is None:
                break

            recovered_ids.append(order["order_id"])
            engine.add_order(order)

        assert recovered_ids == [3, 4, 5]
        assert [
            order["order_id"] for order in engine.buy_orders
        ] == [5, 4, 3]

    finally:
        ring.close()


def test_sustained_order_flow_under_buffer_pressure():
    ring = MMapRingBuffer(size=128)
    engine = MatchingEngine()

    total_orders = 1000
    consumed_ids = []

    def make_order(order_id):
        return {
            "order_id": order_id,
            "side": "BUY",
            "price": 100.0 + (order_id % 10),
            "quantity": 10,
            "timestamp": order_id,
        }

    def consume_orders(count):
        for _ in range(count):
            order = ring.read_order()

            if order is None:
                break

            consumed_ids.append(order["order_id"])
            engine.add_order(order)

    try:
        for order_id in range(1, total_orders + 1):
            order = make_order(order_id)

            # If the buffer is full, consume two orders.
            while not ring.write_order(order):
                consume_orders(2)

        # Process all remaining orders.
        while True:
            order = ring.read_order()

            if order is None:
                break

            consumed_ids.append(order["order_id"])
            engine.add_order(order)

        assert len(consumed_ids) == total_orders
        assert consumed_ids == list(range(1, total_orders + 1))

        assert len(engine.trades) == 0
        assert len(engine.buy_orders) == total_orders

    finally:
        ring.close()
