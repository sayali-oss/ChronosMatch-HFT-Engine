
from datetime import datetime, timezone


class AuditLogger:
    """Stores audit records for executed trades."""

    def __init__(self):
        self.audit_logs = []
        self.next_audit_id = 1

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

    def get_logs(self):
        """Return all audit records."""
        return self.audit_logs.copy()

    def get_total_logs(self):
        """Return the total number of audit records."""
        return len(self.audit_logs)

