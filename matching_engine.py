
import math
import heapq


class _Order:
    """Compact internal representation of an order."""

    __slots__ = (
        "order_id",
        "side",
        "price",
        "quantity",
        "timestamp",
        "remaining",
        "sequence",
        "extra_fields",
    )

    def __init__(self, order, sequence):
        self.order_id = order["order_id"]
        self.side = order["side"]
        self.price = order["price"]
        self.quantity = order["quantity"]
        self.timestamp = order["timestamp"]
        self.remaining = self.quantity
        self.sequence = sequence

        reserved = {
            "order_id",
            "side",
            "price",
            "quantity",
            "timestamp",
            "remaining",
            "sequence",
        }
        extras = {
            key: value
            for key, value in order.items()
            if key not in reserved
        }
        self.extra_fields = extras or None

    def to_dict(self):
        """Return a dictionary compatible with the public order-book API."""
        result = (
            dict(self.extra_fields)
            if self.extra_fields is not None
            else {}
        )
        result.update({
            "order_id": self.order_id,
            "side": self.side,
            "price": self.price,
            "quantity": self.quantity,
            "timestamp": self.timestamp,
            "remaining": self.remaining,
            "sequence": self.sequence,
        })
        return result


class MatchingEngine:
    """Price-time-priority matching engine."""

    def __init__(self):
        self.buy_heap = []
        self.sell_heap = []
        self.trades = []
        self.order_ids = set()
        self.sequence = 0

    @property
    def buy_orders(self):
        """Return BUY orders sorted by best price, then arrival sequence."""
        orders = [entry[2] for entry in self.buy_heap]
        orders.sort(key=lambda order: (-order.price, order.sequence))
        return [order.to_dict() for order in orders]

    @property
    def sell_orders(self):
        """Return SELL orders sorted by best price, then arrival sequence."""
        orders = [entry[2] for entry in self.sell_heap]
        orders.sort(key=lambda order: (order.price, order.sequence))
        return [order.to_dict() for order in orders]

    def add_order(self, order):
        """Validate and process an order. Return its remaining quantity."""
        required = {"order_id", "side", "price", "quantity", "timestamp"}

        if not isinstance(order, dict):
            raise ValueError("order must be a dictionary")

        missing = required - order.keys()
        if missing:
            raise ValueError(f"missing required fields: {sorted(missing)}")

        order_id = order["order_id"]
        side = order["side"]
        price = order["price"]
        quantity = order["quantity"]
        timestamp = order["timestamp"]

        if (
            isinstance(order_id, bool)
            or not isinstance(order_id, int)
            or order_id <= 0
        ):
            raise ValueError("order_id must be a positive integer")

        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or not math.isfinite(price)
            or price <= 0
        ):
            raise ValueError("price must be finite and positive")

        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            raise ValueError("quantity must be a positive integer")

        if order_id in self.order_ids:
            raise ValueError("Duplicate order_id")

        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
        ):
            raise ValueError("timestamp must be finite and numeric")

        next_sequence = self.sequence + 1
        incoming = _Order(order, next_sequence)

        self.sequence = next_sequence
        self.order_ids.add(order_id)

        if side == "BUY":
            self._match_buy(incoming)
        else:
            self._match_sell(incoming)

        if incoming.remaining > 0:
            self._add_to_book(incoming)

        return incoming.remaining

    def _add_to_book(self, order):
        """Add an unmatched order to its side's price-time heap."""
        if order.side == "BUY":
            heapq.heappush(
                self.buy_heap,
                (-order.price, order.sequence, order),
            )
        else:
            heapq.heappush(
                self.sell_heap,
                (order.price, order.sequence, order),
            )

    def _match_buy(self, buy):
        """Match an incoming BUY against the best available SELL orders."""
        while buy.remaining > 0 and self.sell_heap:
            sell = self.sell_heap[0][2]

            if buy.price < sell.price:
                break

            heapq.heappop(self.sell_heap)
            self._execute_trade(buy, sell)

            if sell.remaining > 0:
                self._add_to_book(sell)

    def _match_sell(self, sell):
        """Match an incoming SELL against the best available BUY orders."""
        while sell.remaining > 0 and self.buy_heap:
            buy = self.buy_heap[0][2]

            if buy.price < sell.price:
                break

            heapq.heappop(self.buy_heap)
            self._execute_trade(buy, sell)

            if buy.remaining > 0:
                self._add_to_book(buy)

    def _execute_trade(self, buy, sell):
        """Execute a trade at the resting order's price."""
        traded_quantity = min(buy.remaining, sell.remaining)

        trade_price = (
            buy.price
            if buy.sequence < sell.sequence
            else sell.price
        )

        buy.remaining -= traded_quantity
        sell.remaining -= traded_quantity

        self.trades.append({
            "buy_order_id": buy.order_id,
            "sell_order_id": sell.order_id,
            "price": trade_price,
            "quantity": traded_quantity,
        })

    def get_order_book(self):
        """Return public BUY and SELL order-book snapshots."""
        return {
            "BUY": self.buy_orders,
            "SELL": self.sell_orders,
        }
