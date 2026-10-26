
from firehose.order_generator import generate_order


def test_generate_order():
    order = generate_order(1)

    assert isinstance(order, dict)
    assert order["order_id"] == 1
    assert order["side"] in ["BUY", "SELL"]
    assert isinstance(order["price"], float)
    assert 100.00 <= order["price"] <= 110.00
    assert isinstance(order["quantity"], int)
    assert 1 <= order["quantity"] <= 1000
    assert isinstance(order["timestamp"], int)
    assert order["timestamp"] > 0
