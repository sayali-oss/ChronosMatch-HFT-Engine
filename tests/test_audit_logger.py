
import csv
from datetime import datetime, timezone
from audit_logger import AuditLogger
from matching_engine import MatchingEngine


def test_export_logs_creates_csv_file(tmp_path):
    logger = AuditLogger()

    trade = {
        "buy_order_id": 1,
        "sell_order_id": 2,
        "price": 100,
        "quantity": 5
    }

    logger.log_trade(trade)

    file_path = tmp_path / "audit_report.csv"

    logger.export_logs(file_path)

    assert file_path.exists()


def test_export_logs_contains_correct_trade_data(tmp_path):
    logger = AuditLogger()

    trade = {
        "buy_order_id": 1,
        "sell_order_id": 2,
        "price": 100,
        "quantity": 5
    }

    logger.log_trade(trade)

    file_path = tmp_path / "audit_report.csv"

    logger.export_logs(file_path)

    with file_path.open(
        mode="r",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        reader = csv.DictReader(csvfile)
        records = list(reader)

    assert len(records) == 1
    assert records[0]["buy_order_id"] == "1"
    assert records[0]["sell_order_id"] == "2"
    assert records[0]["price"] == "100"
    assert records[0]["quantity"] == "5"
    assert records[0]["event_type"] == "TRADE_EXECUTED"
    assert records[0]["timestamp"] != ""


def test_export_empty_logs_creates_csv_with_headers(tmp_path):
    logger = AuditLogger()

    file_path = tmp_path / "empty_report.csv"

    logger.export_logs(file_path)

    assert file_path.exists()

    with file_path.open(
        mode="r",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        reader = csv.reader(csvfile)
        headers = next(reader)
        rows = list(reader)

    assert "audit_id" in headers
    assert "timestamp" in headers
    assert rows == []


def test_audit_ids_are_sequential():
    logger = AuditLogger()

    trade1 = {
        "buy_order_id": 1,
        "sell_order_id": 2,
        "price": 100,
        "quantity": 5
    }

    trade2 = {
        "buy_order_id": 3,
        "sell_order_id": 4,
        "price": 105,
        "quantity": 3
    }

    record1 = logger.log_trade(trade1)
    record2 = logger.log_trade(trade2)

    assert record1["audit_id"] == 1
    assert record2["audit_id"] == 2


def test_total_audit_log_count_is_correct():
    logger = AuditLogger()

    trades = [
        {"buy_order_id": 1, "sell_order_id": 2,
         "price": 100, "quantity": 5},

        {"buy_order_id": 3, "sell_order_id": 4,
         "price": 105, "quantity": 3},

        {"buy_order_id": 5, "sell_order_id": 6,
         "price": 110, "quantity": 2}
    ]

    for trade in trades:
        logger.log_trade(trade)

    assert logger.get_total_logs() == 3
    assert len(logger.get_logs()) == 3


def test_audit_record_preserves_trade_data():
    logger = AuditLogger()

    trade = {
        "buy_order_id": 10,
        "sell_order_id": 20,
        "price": 150,
        "quantity": 8
    }

    record = logger.log_trade(trade)

    assert record["buy_order_id"] == 10
    assert record["sell_order_id"] == 20
    assert record["price"] == 150
    assert record["quantity"] == 8
    assert record["event_type"] == "TRADE_EXECUTED"


def test_repeated_engine_collection_does_not_duplicate_trades():
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

    assert logger.get_total_logs() == 1

    # Collecting the same engine trades again
    logger.log_engine_trades(engine)

    assert logger.get_total_logs() == 1


def test_get_logs_returns_separate_list():
    logger = AuditLogger()

    trade = {
        "buy_order_id": 1,
        "sell_order_id": 2,
        "price": 100,
        "quantity": 5
    }

    logger.log_trade(trade)

    returned_logs = logger.get_logs()

    # Modify the returned list
    returned_logs.clear()

    # Internal audit records should remain unchanged
    assert logger.get_total_logs() == 1
