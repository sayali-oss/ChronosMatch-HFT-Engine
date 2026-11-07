
import csv
from datetime import datetime, timezone
from pathlib import Path


class AuditLogger:
    """Stores and exports audit records for executed trades."""

    def __init__(self):
        self.audit_logs = []
        self.next_audit_id = 1
        self.processed_trade_count = 0

    def log_trade(self, trade):
        """Create an audit record for an executed trade."""

        required_fields = {
            "buy_order_id",
            "sell_order_id",
            "price",
            "quantity"
        }

        if not isinstance(trade, dict):
            raise ValueError("Trade must be a dictionary")

        missing = required_fields - trade.keys()

        if missing:
            raise ValueError(
                f"Missing trade fields: {sorted(missing)}"
            )

        audit_record = {
            "audit_id": self.next_audit_id,
            "event_type": "TRADE_EXECUTED",
            "buy_order_id": trade["buy_order_id"],
            "sell_order_id": trade["sell_order_id"],
            "price": trade["price"],
            "quantity": trade["quantity"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.audit_logs.append(audit_record)
        self.next_audit_id += 1

        return audit_record

    def log_engine_trades(self, engine):
        """Collect newly executed trades from the matching engine."""

        if not hasattr(engine, "trades"):
            raise ValueError("Engine must have a trades attribute")

        if not isinstance(engine.trades, list):
            raise ValueError("Engine trades must be a list")

        new_trades = engine.trades[self.processed_trade_count:]

        new_records = []

        for trade in new_trades:
            record = self.log_trade(trade)
            new_records.append(record)
            self.processed_trade_count += 1

        return new_records

    def get_logs(self):
        """Return all audit records."""
        return self.audit_logs.copy()

    def get_total_logs(self):
        """Return the total number of audit records."""
        return len(self.audit_logs)

    def export_logs(self, filename):
        """Export audit records to a CSV file."""

        fieldnames = [
            "audit_id",
            "event_type",
            "buy_order_id",
            "sell_order_id",
            "price",
            "quantity",
            "timestamp"
        ]

        file_path = Path(filename)

        with file_path.open(
            mode="w",
            newline="",
            encoding="utf-8"
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(self.audit_logs)

        return str(file_path)
