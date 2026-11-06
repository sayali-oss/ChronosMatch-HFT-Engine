from datetime import datetime, timezone
from audit_logger import AuditLogger
from matching_engine import MatchingEngine


def test_timestamp_is_valid_iso_format():
    logger = AuditLogger()

    trade = {
        "buy_order_id": 1,
        "sell_order_id": 2,
        "price": 100,
        "quantity": 5
    }

    record = logger.log_trade(trade)

    parsed_time = datetime.fromisoformat(record["timestamp"])

    assert isinstance(parsed_time, datetime)


def test_timestamp_uses_utc_timezone():
    logger = AuditLogger()

    trade = {
        "buy_order_id": 1,
        "sell_order_id": 2,
        "price": 100,
        "quantity": 5
    }

    record = logger.log_trade(trade)

    parsed_time = datetime.fromisoformat(record["timestamp"])

    assert parsed_time.tzinfo is not None
    assert parsed_time.utcoffset() == timezone.utc.utcoffset(parsed_time)


def test_every_executed_trade_has_timestamp():
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

    logger.log_engine_trades(engine)

    records = logger.get_logs()

    assert len(records) == 1

    for record in records:
        parsed_time = datetime.fromisoformat(record["timestamp"])

        assert parsed_time.tzinfo is not None
        assert parsed_time.utcoffset() == timezone.utc.utcoffset(parsed_time)