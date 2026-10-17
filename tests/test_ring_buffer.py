
import unittest

from mmap_ring_buffer import MMapRingBuffer


def make_order(order_id):
    return {
        "order_id": order_id,
        "side": "BUY" if order_id % 2 else "SELL",
        "price": 100.00 + order_id,
        "quantity": order_id * 10,
        "timestamp": 1_000_000 + order_id,
    }


class TestMMapRingBuffer(unittest.TestCase):

    def test_empty_buffer(self):
        ring = MMapRingBuffer(size=64)
        try:
            self.assertIsNone(ring.read_order())
        finally:
            ring.close()

    def test_write_and_read_order(self):
        ring = MMapRingBuffer(size=64)
        order = make_order(1)

        try:
            self.assertTrue(ring.write_order(order))
            self.assertEqual(ring.read_order(), order)
            self.assertIsNone(ring.read_order())
        finally:
            ring.close()

    def test_full_buffer(self):
        # 64 bytes / 32 bytes per record = 2 slots.
        # One slot must remain unused to distinguish full from empty.
        ring = MMapRingBuffer(size=64)

        try:
            self.assertTrue(ring.write_order(make_order(1)))
            self.assertFalse(ring.write_order(make_order(2)))
            self.assertEqual(ring.read_order(), make_order(1))

            # Space is available again after reading.
            self.assertTrue(ring.write_order(make_order(2)))
            self.assertEqual(ring.read_order(), make_order(2))
        finally:
            ring.close()

    def test_wraparound(self):
        ring = MMapRingBuffer(size=64)

        try:
            self.assertTrue(ring.write_order(make_order(1)))
            self.assertEqual(ring.read_order(), make_order(1))

            self.assertTrue(ring.write_order(make_order(2)))
            self.assertEqual(ring.read_order(), make_order(2))

            # The head and tail have wrapped around the buffer.
            self.assertTrue(ring.write_order(make_order(3)))
            self.assertEqual(ring.read_order(), make_order(3))
        finally:
            ring.close()

    def test_order_integrity(self):
        ring = MMapRingBuffer(size=128)
        orders = [make_order(i) for i in range(1, 4)]

        try:
            for order in orders:
                self.assertTrue(ring.write_order(order))

            recovered = [ring.read_order() for _ in orders]
            self.assertEqual(recovered, orders)
        finally:
            ring.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
