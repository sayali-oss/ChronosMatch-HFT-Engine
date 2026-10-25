
import pytest
from matching_engine import MatchingEngine


def make_order(order_id, side, price, quantity):
    return {
        "order_id": order_id,
        "side": side,
        "price": price,
        "quantity": quantity,
        "timestamp": order_id,
    }


def test_matching_buy_and_sell():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 100, 10))
    engine.add_order(make_order(2, "BUY", 101, 4))

    assert len(engine.trades) == 1
    assert engine.trades[0]["buy_order_id"] == 2
    assert engine.trades[0]["sell_order_id"] == 1
    assert engine.trades[0]["price"] == 100
    assert engine.trades[0]["quantity"] == 4
    assert engine.sell_orders[0]["remaining"] == 6


def test_no_match_when_prices_are_incompatible():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 105, 5))
    engine.add_order(make_order(2, "BUY", 100, 5))

    assert len(engine.trades) == 0
    assert len(engine.buy_orders) == 1
    assert len(engine.sell_orders) == 1


def test_partial_fill_across_multiple_sell_orders():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 100, 2))
    engine.add_order(make_order(2, "SELL", 101, 3))
    engine.add_order(make_order(3, "BUY", 102, 4))

    assert len(engine.trades) == 2
    assert [t["quantity"] for t in engine.trades] == [2, 2]
    assert engine.trades[0]["price"] == 100
    assert engine.trades[1]["price"] == 101
    assert engine.sell_orders[0]["order_id"] == 2
    assert engine.sell_orders[0]["remaining"] == 1


def test_price_time_priority():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 100, 2))
    engine.add_order(make_order(2, "SELL", 100, 3))
    engine.add_order(make_order(3, "BUY", 100, 4))

    assert engine.trades[0]["sell_order_id"] == 1
    assert engine.trades[1]["sell_order_id"] == 2
    assert engine.trades[0]["quantity"] == 2
    assert engine.trades[1]["quantity"] == 2


def test_invalid_order_is_rejected():
    engine = MatchingEngine()

    with pytest.raises(ValueError):
        engine.add_order(make_order(1, "HOLD", 100, 5))

    with pytest.raises(ValueError):
        engine.add_order(make_order(2, "BUY", -1, 5))

    with pytest.raises(ValueError):
        engine.add_order(make_order(3, "BUY", 100, 0))


def test_sell_orders_are_inserted_in_ascending_price_order():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 105, 2))
    engine.add_order(make_order(2, "SELL", 100, 3))
    engine.add_order(make_order(3, "SELL", 102, 4))

    assert [o["price"] for o in engine.sell_orders] == [
        100, 102, 105
    ]


def test_sell_orders_with_equal_prices_keep_fifo_priority():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 100, 2))
    engine.add_order(make_order(2, "SELL", 100, 3))
    engine.add_order(make_order(3, "BUY", 100, 4))

    assert engine.trades[0]["sell_order_id"] == 1
    assert engine.trades[1]["sell_order_id"] == 2


def test_sell_order_matches_multiple_buy_orders():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "BUY", 105, 2))
    engine.add_order(make_order(2, "BUY", 103, 3))
    engine.add_order(make_order(3, "SELL", 100, 4))

    assert len(engine.trades) == 2
    assert [t["buy_order_id"] for t in engine.trades] == [1, 2]
    assert [t["quantity"] for t in engine.trades] == [2, 2]
    assert engine.buy_orders[0]["order_id"] == 2
    assert engine.buy_orders[0]["remaining"] == 1


def test_order_book_shows_best_prices_first():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "BUY", 100, 2))
    engine.add_order(make_order(2, "BUY", 105, 3))
    engine.add_order(make_order(3, "SELL", 110, 4))
    engine.add_order(make_order(4, "SELL", 108, 5))

    book = engine.get_order_book()

    assert [o["price"] for o in book["BUY"]] == [105, 100]
    assert [o["price"] for o in book["SELL"]] == [108, 110]



def test_duplicate_order_id_is_rejected():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "BUY", 100, 5))

    with pytest.raises(ValueError, match="Duplicate"):
        engine.add_order(make_order(1, "SELL", 100, 5))


@pytest.mark.parametrize("price", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_price_is_rejected(price):
    engine = MatchingEngine()

    with pytest.raises(ValueError):
        engine.add_order(make_order(1, "BUY", price, 5))


def test_missing_required_field_is_rejected():
    engine = MatchingEngine()
    order = make_order(1, "BUY", 100, 5)
    del order["timestamp"]

    with pytest.raises(ValueError, match="missing required"):
        engine.add_order(order)


def test_invalid_timestamp_is_rejected():
    engine = MatchingEngine()
    order = make_order(1, "BUY", 100, 5)
    order["timestamp"] = float("nan")

    with pytest.raises(ValueError, match="timestamp"):
        engine.add_order(order)


def test_invalid_order_does_not_consume_order_id():
    engine = MatchingEngine()

    with pytest.raises(ValueError):
        engine.add_order(make_order(1, "BUY", -100, 5))

    # A valid order with the same ID should still be accepted.
    assert engine.add_order(make_order(1, "BUY", 100, 5)) == 5
    assert len(engine.buy_orders) == 1


def test_unmatched_order_remains_in_order_book():
    engine = MatchingEngine()

    remaining = engine.add_order(make_order(1, "BUY", 90, 7))

    assert remaining == 7
    assert len(engine.trades) == 0
    assert engine.buy_orders[0]["remaining"] == 7


def test_invalid_order_type_is_rejected():
    engine = MatchingEngine()

    with pytest.raises(ValueError, match="dictionary"):
        engine.add_order(None)
