class MatchingEngine:
    """
    Simple Limit Order Book with price-time priority.

    BUY orders match the lowest available SELL price.
    SELL orders match the highest available BUY price.
    Earlier orders at the same price get priority.
    """

    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.trades = []
        self.sequence = 0

    def add_order(self, order):
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
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            raise ValueError("price must be numeric")
        if price <= 0:
            raise ValueError("price must be positive")
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if type(order_id) is not int or order_id <= 0:
            raise ValueError("order_id must be a positive integer")

        self.sequence += 1
        incoming = {
            **order,
            "remaining": quantity,
            "sequence": self.sequence
        }

        if side == "BUY":
            self._match_buy(incoming)
        else:
            self._match_sell(incoming)

        # Store any unfilled quantity in the appropriate book.
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
            # Best ask is the lowest-priced sell order.
            best_sell = min(
                self.sell_orders,
                key=lambda o: (o["price"], o["sequence"])
            )

            if buy["price"] < best_sell["price"]:
                break

            self._execute_trade(buy, best_sell, best_sell["price"])

            if best_sell["remaining"] == 0:
                self.sell_orders.remove(best_sell)

    def _match_sell(self, sell):
        while sell["remaining"] > 0 and self.buy_orders:
            # Best bid is the highest-priced buy order.
            best_buy = max(
                self.buy_orders,
                key=lambda o: (o["price"], -o["sequence"])
            )

            if sell["price"] > best_buy["price"]:
                break

            self._execute_trade(sell, best_buy, best_buy["price"])

            if best_buy["remaining"] == 0:
                self.buy_orders.remove(best_buy)

    def _execute_trade(self, incoming, resting, execution_price):
        quantity = min(
            incoming["remaining"],
            resting["remaining"]
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
            "quantity": quantity
        }

        self.trades.append(trade)
        print("TRADE:", trade)

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
                {k: o[k] for k in
                 ("order_id", "price", "remaining")}
                for o in self.buy_orders
            ],
            "SELL": [
                {k: o[k] for k in
                 ("order_id", "price", "remaining")}
                for o in self.sell_orders
            ]
        }


if __name__ == "__main__":
    engine = MatchingEngine()

    engine.add_order({
        "order_id": 1,
        "side": "SELL",
        "price": 100.0,
        "quantity": 10,
        "timestamp": 1
    })

    engine.add_order({
        "order_id": 2,
        "side": "BUY",
        "price": 101.0,
        "quantity": 4,
        "timestamp": 2
    })

    print("\nRemaining order book:")
    print(engine.get_order_book())

    print("\nAll trades:")
    print(engine.trades)