
from audit_logger import AuditLogger
from matching_engine import MatchingEngine


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


def test_matching_engine_trade_is_audited():
    engine = MatchingEngine()
    logger = AuditLogger()

    engine.add_order({
        "order_id": 1,
        "side": "SELL",
        "price": 100,
        "quantity": 10,
        "timestamp": 1
    })

    engine.add_order({
        "order_id": 2,
        "side": "BUY",
        "price": 101,
        "quantity": 4,
        "timestamp": 2
    })

    records = logger.log_engine_trades(engine)

    assert len(records) == 1
    assert records[0]["buy_order_id"] == 2
    assert records[0]["sell_order_id"] == 1
    assert records[0]["price"] == 100
    assert records[0]["quantity"] == 4


def test_multiple_executed_trades_are_audited():
    engine = MatchingEngine()
    logger = AuditLogger()

    engine.add_order({
        "order_id": 1,
        "side": "SELL",
        "price": 100,
        "quantity": 5,
        "timestamp": 1
    })

    engine.add_order({
        "order_id": 2,
        "side": "BUY",
        "price": 100,
        "quantity": 5,
        "timestamp": 2
    })

    engine.add_order({
        "order_id": 3,
        "side": "SELL",
        "price": 105,
        "quantity": 3,
        "timestamp": 3
    })

    engine.add_order({
        "order_id": 4,
        "side": "BUY",
        "price": 105,
        "quantity": 3,
        "timestamp": 4
    })

    records = logger.log_engine_trades(engine)

    assert len(records) == 2
    assert logger.get_total_logs() == 2
    assert records[0]["audit_id"] == 1
    assert records[1]["audit_id"] == 2


def test_repeated_calls_do_not_duplicate_audit_records():
    engine = MatchingEngine()
    logger = AuditLogger()

    engine.add_order({
        "order_id": 1,
        "side": "SELL",
        "price": 100,
        "quantity": 5,
        "timestamp": 1
    })

    engine.add_order({
        "order_id": 2,
        "side": "BUY",
        "price": 100,
        "quantity": 5,
        "timestamp": 2
    })

    logger.log_engine_trades(engine)

    # Calling again should not duplicate the previous trade.
    logger.log_engine_trades(engine)

    assert logger.get_total_logs() == 1


def test_new_trades_are_logged_on_later_calls():
    engine = MatchingEngine()
    logger = AuditLogger()

    engine.add_order({
        "order_id": 1,
        "side": "SELL",
        "price": 100,
        "quantity": 5,
        "timestamp": 1
    })

    engine.add_order({
        "order_id": 2,
        "side": "BUY",
        "price": 100,
        "quantity": 5,
        "timestamp": 2
    })

    logger.log_engine_trades(engine)

    engine.add_order({
        "order_id": 3,
        "side": "SELL",
        "price": 105,
        "quantity": 3,
        "timestamp": 3
    })

    engine.add_order({
        "order_id": 4,
        "side": "BUY",
        "price": 105,
        "quantity": 3,
        "timestamp": 4
    })

    logger.log_engine_trades(engine)

    assert logger.get_total_logs() == 2
    assert logger.get_logs()[0]["audit_id"] == 1
    assert logger.get_logs()[1]["audit_id"] == 2
