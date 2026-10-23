
import pytest
from matching_engine import MatchingEngine


def make_order(order_id, side, price, quantity):
    return {
        "order_id": order_id,
        "side": side,
        "price": price,
        "quantity": quantity,
        "timestamp": order_id
    }


def test_matching_buy_and_sell():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 100, 10))
    engine.add_order(make_order(2, "BUY", 101, 4))

    assert len(engine.trades) == 1
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
    assert [trade["quantity"] for trade in engine.trades] == [2, 2]
    assert engine.sell_orders[0]["order_id"] == 2
    assert engine.sell_orders[0]["remaining"] == 1


def test_price_time_priority():
    engine = MatchingEngine()

    engine.add_order(make_order(1, "SELL", 100, 2))
    engine.add_order(make_order(2, "SELL", 100, 3))
    engine.add_order(make_order(3, "BUY", 100, 4))

    assert engine.trades[0]["sell_order_id"] == 1
    assert engine.trades[1]["sell_order_id"] == 2


def test_invalid_order_is_rejected():
    engine = MatchingEngine()

    with pytest.raises(ValueError):
        engine.add_order(make_order(1, "HOLD", 100, 5))

    with pytest.raises(ValueError):
        engine.add_order(make_order(2, "BUY", -1, 5))

    with pytest.raises(ValueError):
        engine.add_order(make_order(3, "BUY", 100, 0))
