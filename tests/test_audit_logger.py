
from audit_logger import AuditLogger


def test_audit_log_creation():
    logger = AuditLogger()

    trade = {
        "buy_order_id": 2,
        "sell_order_id": 1,
        "price": 100,
        "quantity": 4
    }

    record = logger.log_trade(trade)

    assert record["audit_id"] == 1
    assert record["event_type"] == "TRADE_EXECUTED"
    assert record["buy_order_id"] == 2
    assert record["sell_order_id"] == 1
    assert record["price"] == 100
    assert record["quantity"] == 4
    assert "timestamp" in record


def test_multiple_audit_records():
    logger = AuditLogger()

    trade1 = {
        "buy_order_id": 2,
        "sell_order_id": 1,
        "price": 100,
        "quantity": 4
    }

    trade2 = {
        "buy_order_id": 4,
        "sell_order_id": 3,
        "price": 105,
        "quantity": 2
    }

    logger.log_trade(trade1)
    logger.log_trade(trade2)

    assert logger.get_total_logs() == 2
    assert logger.get_logs()[0]["audit_id"] == 1
    assert logger.get_logs()[1]["audit_id"] == 2


def test_invalid_trade_is_rejected():
    logger = AuditLogger()

    try:
        logger.log_trade({"price": 100})
        assert False, "Expected ValueError"
    except ValueError:
        pass

