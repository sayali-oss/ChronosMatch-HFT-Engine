
import mmap
import struct


class MMapRingBuffer:
    """
    Fixed-size memory-mapped ring buffer for trading orders.

    Record format: <IB3xqIQ4x
    Total record size: 32 bytes
    """

    def __init__(self, size: int = 1024):
        self.struct_format = "<IB3xqIQ4x"
        self.msg_size = struct.calcsize(self.struct_format)

        if size < 2 * self.msg_size:
            raise ValueError(
                f"Buffer must be at least {2 * self.msg_size} bytes"
            )

        if size % self.msg_size != 0:
            raise ValueError(
                f"Buffer size must be a multiple of {self.msg_size}"
            )

        self.size = size
        self.mmap_file = mmap.mmap(-1, size)
        self.head = 0
        self.tail = 0

    def write_order(self, order: dict) -> bool:
        """Write a complete order. Return False if the buffer is full."""

        required_fields = {
            "order_id", "side", "price", "quantity", "timestamp"
        }

        if not required_fields.issubset(order):
            raise ValueError("Order is missing required fields")

        order_id = order["order_id"]
        side = order["side"]
        price = order["price"]
        quantity = order["quantity"]
        timestamp = order["timestamp"]

        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        # Store prices as integer cents to avoid floating-point encoding.
        price_cents = round(price * 100)

        if price_cents <= 0:
            raise ValueError("price must be positive")

        if not 1 <= order_id <= 0xFFFFFFFF:
            raise ValueError("order_id is outside the supported range")

        if not 1 <= quantity <= 0xFFFFFFFF:
            raise ValueError("quantity is outside the supported range")

        if not 0 <= timestamp <= 0xFFFFFFFFFFFFFFFF:
            raise ValueError("timestamp is outside the supported range")

        side_code = 0 if side == "BUY" else 1

        packed_data = struct.pack(
            self.struct_format,
            order_id,
            side_code,
            price_cents,
            quantity,
            timestamp
        )

        next_head = (self.head + self.msg_size) % self.size

        if next_head == self.tail:
            return False

        self.mmap_file.seek(self.head)
        self.mmap_file.write(packed_data)
        self.head = next_head

        return True

    def read_order(self):
        """Read the oldest order, or return None if empty."""

        if self.head == self.tail:
            return None

        self.mmap_file.seek(self.tail)
        packed_data = self.mmap_file.read(self.msg_size)

        order_id, side_code, price_cents, quantity, timestamp = (
            struct.unpack(self.struct_format, packed_data)
        )

        self.tail = (self.tail + self.msg_size) % self.size

        return {
            "order_id": order_id,
            "side": "BUY" if side_code == 0 else "SELL",
            "price": price_cents / 100,
            "quantity": quantity,
            "timestamp": timestamp
        }

    def close(self):
        self.mmap_file.close()


if __name__ == "__main__":
    ring = MMapRingBuffer(size=1024)

    test_order = {
        "order_id": 1,
        "side": "BUY",
        "price": 105.25,
        "quantity": 100,
        "timestamp": 123456789
    }

    try:
        print("Record size:", ring.msg_size, "bytes")

        if ring.write_order(test_order):
            print("Written:", test_order)

        recovered_order = ring.read_order()
        print("Read back:", recovered_order)

        assert recovered_order == test_order
        print("Round-trip test passed!")

    finally:
        ring.close()
