
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

    # Create the required-field set only once, not for every order.
    REQUIRED_FIELDS = frozenset({
        "order_id",
        "side",
        "price",
        "quantity",
        "timestamp",
    })

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

        # Validate the order structure.
        if not isinstance(order, dict):
            raise ValueError("Order must be a dictionary")

        if not self.REQUIRED_FIELDS.issubset(order):
            raise ValueError("Order is missing required fields")

        # Extract the required fields.
        order_id = order["order_id"]
        side = order["side"]
        price = order["price"]
        quantity = order["quantity"]
        timestamp = order["timestamp"]

        # Validate order side.
        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        # Validate price.
        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or not math.isfinite(price)
            or price <= 0
        ):
            raise ValueError("price must be a finite positive number")

        # Validate quantity.
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")

        # Validate order ID.
        if type(order_id) is not int or order_id <= 0:
            raise ValueError("order_id must be a positive integer")

        if order_id in self.order_ids:
            raise ValueError("Duplicate order_id")

        # Validate timestamp.
        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
        ):
            raise ValueError("timestamp must be finite and numeric")

        # Create the internal order representation.
        incoming = {
            **order,
            "remaining": quantity,
            "sequence": self.sequence + 1,
        }

        # Register only after all validation succeeds.
        self.sequence += 1
        self.order_ids.add(order_id)

        # Match the incoming order against the opposite side.
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
        """Match an incoming BUY order against SELL orders."""

        while self._sell_heap and buy["remaining"] > 0:
            best_sell = self._sell_heap[0][2]

            # No match if the BUY price is too low.
            if buy["price"] < best_sell["price"]:
                break

            heapq.heappop(self._sell_heap)
            self._execute_trade(buy, best_sell)

            # Reinsert any partially filled SELL order.
            if best_sell["remaining"] > 0:
                self._add_to_book(best_sell)

    def _match_sell(self, sell):
        """Match an incoming SELL order against BUY orders."""

        while self._buy_heap and sell["remaining"] > 0:
            best_buy = self._buy_heap[0][2]

            # No match if the SELL price is too high.
            if sell["price"] > best_buy["price"]:
                break

            heapq.heappop(self._buy_heap)
            self._execute_trade(best_buy, sell)

            # Reinsert any partially filled BUY order.
            if best_buy["remaining"] > 0:
                self._add_to_book(best_buy)

    def _execute_trade(self, buy, sell):
        """Execute a trade and update the remaining quantities."""

        traded_quantity = min(
            buy["remaining"],
            sell["remaining"],
        )

        # Execute at the price of the resting order.
        if buy["sequence"] < sell["sequence"]:
            trade_price = buy["price"]
        else:
            trade_price = sell["price"]

        buy["remaining"] -= traded_quantity
        sell["remaining"] -= traded_quantity

        self.trades.append({
            "buy_order_id": buy["order_id"],
            "sell_order_id": sell["order_id"],
            "price": trade_price,
            "quantity": traded_quantity,
        })

    def get_order_book(self):
        """Return the current BUY and SELL order-book snapshots."""

        return {
            "BUY": self.buy_orders,
            "SELL": self.sell_orders,
        }
