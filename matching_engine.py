
import heapq
import math


class MatchingEngine:
    """
    Limit Order Book using heaps and price-time priority.

    BUY orders:
        Highest price first, then earliest arrival.

    SELL orders:
        Lowest price first, then earliest arrival.

    The public buy_orders and sell_orders attributes return
    price-time-sorted snapshots for compatibility with existing tests.
    """

    def __init__(self):
        self._buy_heap = []
        self._sell_heap = []
        self.trades = []
        self.sequence = 0
        self.order_ids = set()

    @property
    def buy_orders(self):
        """Return BUY orders in price-time priority."""
        return [
            entry[2]
            for entry in sorted(self._buy_heap)
        ]

    @property
    def sell_orders(self):
        """Return SELL orders in price-time priority."""
        return [
            entry[2]
            for entry in sorted(self._sell_heap)
        ]

    def add_order(self, order):
        """Validate, match, and store an incoming order."""

        if not isinstance(order, dict):
            raise ValueError("Order must be a dictionary")

        required = {
            "order_id",
            "side",
            "price",
            "quantity",
            "timestamp",
        }

        if not required.issubset(order):
            raise ValueError("Order is missing required fields")

        order_id = order["order_id"]
        side = order["side"]
        price = order["price"]
        quantity = order["quantity"]
        timestamp = order["timestamp"]

        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or not math.isfinite(price)
            or price <= 0
        ):
            raise ValueError("price must be a finite positive number")

        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")

        if type(order_id) is not int or order_id <= 0:
            raise ValueError("order_id must be a positive integer")

        if order_id in self.order_ids:
            raise ValueError("Duplicate order_id")

        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
        ):
            raise ValueError("timestamp must be finite and numeric")

        incoming = {
            **order,
            "remaining": quantity,
            "sequence": self.sequence + 1,
        }

        # Register only after all validation succeeds.
        self.sequence += 1
        self.order_ids.add(order_id)

        if side == "BUY":
            self._match_buy(incoming)
        else:
            self._match_sell(incoming)

        # Add any remaining quantity to its heap.
        if incoming["remaining"] > 0:
            self._add_to_book(incoming)

        return incoming["remaining"]

    def _add_to_book(self, order):
        """Insert an order into the appropriate priority heap."""

        if order["side"] == "BUY":
            # Negative price makes the highest BUY price come first.
            entry = (
                -order["price"],
                order["sequence"],
                order,
            )
            heapq.heappush(self._buy_heap, entry)

        else:
            # Lowest SELL price comes first.
            entry = (
                order["price"],
                order["sequence"],
                order,
            )
            heapq.heappush(self._sell_heap, entry)

    def _match_buy(self, buy):
        """Match a BUY order against the best available SELL orders."""

        while buy["remaining"] > 0 and self._sell_heap:
            best_sell = self._sell_heap[0][2]

            if buy["price"] < best_sell["price"]:
                break

            self._execute_trade(
                buy,
                best_sell,
                best_sell["price"],
            )

            if best_sell["remaining"] == 0:
                heapq.heappop(self._sell_heap)

    def _match_sell(self, sell):
        """Match a SELL order against the best available BUY orders."""

        while sell["remaining"] > 0 and self._buy_heap:
            best_buy = self._buy_heap[0][2]

            if sell["price"] > best_buy["price"]:
                break

            self._execute_trade(
                sell,
                best_buy,
                best_buy["price"],
            )

            if best_buy["remaining"] == 0:
                heapq.heappop(self._buy_heap)

    def _execute_trade(self, incoming, resting, execution_price):
        """Execute a trade and update the remaining quantities."""

        quantity = min(
            incoming["remaining"],
            resting["remaining"],
        )

        incoming["remaining"] -= quantity
        resting["remaining"] -= quantity

        trade = {
            "buy_order_id": (
                incoming["order_id"]
                if incoming["side"] == "BUY"
                else resting["order_id"]
            ),
            "sell_order_id": (
                incoming["order_id"]
                if incoming["side"] == "SELL"
                else resting["order_id"]
            ),
            "price": execution_price,
            "quantity": quantity,
        }

        self.trades.append(trade)

    def get_order_book(self):
        """Return a readable snapshot of the current order book."""

        return {
            "BUY": [
                {
                    "order_id": order["order_id"],
                    "price": order["price"],
                    "remaining": order["remaining"],
                }
                for order in self.buy_orders
            ],
            "SELL": [
                {
                    "order_id": order["order_id"],
                    "price": order["price"],
                    "remaining": order["remaining"],
                }
                for order in self.sell_orders
            ],
        }


if __name__ == "__main__":
    engine = MatchingEngine()

    engine.add_order({
        "order_id": 1,
        "side": "SELL",
        "price": 100.0,
        "quantity": 10,
        "timestamp": 1,
    })

    engine.add_order({
        "order_id": 2,
        "side": "BUY",
        "price": 101.0,
        "quantity": 4,
        "timestamp": 2,
    })

    print("Remaining order book:")
    print(engine.get_order_book())

    print("\nTrades executed:")
    for trade in engine.trades:
        print(trade)
