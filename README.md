# ChronosMatch-HFT-Engine
Zero-Copy high-frequency Trading ENgine in python
"""
Basic Order Book Skeleton using Python dict and lists.
Supports adding buy/sell orders and viewing current book state.
"""

from collections import defaultdict

class OrderBook:
    def __init__(self):
        # Separate books for bids (buy) and asks (sell)
        # Keys are price levels, values are lists of orders at that price
        self.bids = defaultdict(list)  # Buy orders
        self.asks = defaultdict(list)  # Sell orders

    def add_order(self, side, price, quantity, order_id):
        """
        Add an order to the book.
        :param side: 'buy' or 'sell'
        :param price: float or int price level
        :param quantity: float or int quantity
        :param order_id: unique identifier for the order
        """
        if side not in ('buy', 'sell'):
            raise ValueError("Side must be 'buy' or 'sell'")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")

        order = {"id": order_id, "price": price, "qty": quantity}

        if side == 'buy':
            self.bids[price].append(order)
        else:
            self.asks[price].append(order)

    def remove_order(self, side, order_id):
        """
        Remove an order by ID from the book.
        """
        book = self.bids if side == 'buy' else self.asks
        for price in list(book.keys()):
            book[price] = [o for o in book[price] if o["id"] != order_id]
            if not book[price]:  # Remove empty price levels
                del book[price]

    def get_best_bid(self):
        """Return highest bid price and total quantity."""
        if not self.bids:
            return None
        best_price = max(self.bids.keys())
        total_qty = sum(o["qty"] for o in self.bids[best_price])
        return best_price, total_qty

    def get_best_ask(self):
        """Return lowest ask price and total quantity."""
        if not self.asks:
            return None
        best_price = min(self.asks.keys())
        total_qty = sum(o["qty"] for o in self.asks[best_price])
        return best_price, total_qty

    def display_book(self):
        """Print current order book state."""
        print("\n--- ORDER BOOK ---")
        print("SELL (asks):")
        for price in sorted(self.asks.keys()):
            qty = sum(o["qty"] for o in self.asks[price])
            print(f"  Price: {price} | Qty: {qty}")

        print("BUY (bids):")
        for price in sorted(self.bids.keys(), reverse=True):
            qty = sum(o["qty"] for o in self.bids[price])
            print(f"  Price: {price} | Qty: {qty}")
        print("------------------\n")


# Example usage
if __name__ == "__main__":
    ob = OrderBook()
    ob.add_order('buy', 100, 5, 'B1')
    ob.add_order('buy', 101, 3, 'B2')
    ob.add_order('sell', 105, 2, 'S1')
    ob.add_order('sell', 104, 4, 'S2')

    ob.display_book()

    print("Best Bid:", ob.get_best_bid())
    print("Best Ask:", ob.get_best_ask())

    ob.remove_order('buy', 'B1')
    ob.display_book()
