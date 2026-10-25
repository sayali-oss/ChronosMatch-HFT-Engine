
import math


class MatchingEngine:
    """
    Limit Order Book with price-time priority.

    BUY orders match the lowest available SELL price.
    SELL orders match the highest available BUY price.
    Earlier orders at the same price get priority.
    """

    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.trades = []
        self.sequence = 0
        self.order_ids = set()

    def add_order(self, order):
        if not isinstance(order, dict):
            raise ValueError("Order must be a dictionary")

        required = {
            "order_id", "side", "price", "quantity", "timestamp"
        }

        if not required.issubset(order):
            raise ValueError("Order is missing required fields")

        side = order["side"]
        price = order["price"]
        quantity = order["quantity"]
        order_id = order["order_id"]

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

        timestamp = order["timestamp"]
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

        if incoming["remaining"] > 0:
            book = (
                self.buy_orders if side == "BUY"
                else self.sell_orders
            )
            book.append(incoming)

        self._sort_books()
        return incoming["remaining"]

    def _match_buy(self, buy):
        while buy["remaining"] > 0 and self.sell_orders:
            best_sell = self.sell_orders[0]

            if buy["price"] < best_sell["price"]:
                break

            self._execute_trade(buy, best_sell, best_sell["price"])

            if best_sell["remaining"] == 0:
                self.sell_orders.pop(0)

    def _match_sell(self, sell):
        while sell["remaining"] > 0 and self.buy_orders:
            best_buy = self.buy_orders[0]

            if sell["price"] > best_buy["price"]:
                break

            self._execute_trade(sell, best_buy, best_buy["price"])

            if best_buy["remaining"] == 0:
                self.buy_orders.pop(0)

    def _execute_trade(self, incoming, resting, execution_price):
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

    def _sort_books(self):
        self.buy_orders.sort(
            key=lambda o: (-o["price"], o["sequence"])
        )
        self.sell_orders.sort(
            key=lambda o: (o["price"], o["sequence"])
        )

    def get_order_book(self):
        return {
            "BUY": [
                {
                    "order_id": o["order_id"],
                    "price": o["price"],
                    "remaining": o["remaining"],
                }
                for o in self.buy_orders
            ],
            "SELL": [
                {
                    "order_id": o["order_id"],
                    "price": o["price"],
                    "remaining": o["remaining"],
                }
                for o in self.sell_orders
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

    print("All trades:")
    print(engine.trades)
