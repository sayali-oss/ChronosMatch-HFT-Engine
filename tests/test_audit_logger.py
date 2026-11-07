
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
