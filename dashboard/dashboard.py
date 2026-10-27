import curses
import json
import time

latency_history = []
total_orders_processed = 0
dashboard_refreshes = 0


def read_latest_json(filename="engine.json"):
    try:
        with open(filename, "r") as file:
            lines = file.readlines()

            if not lines:
                return None

            return json.loads(lines[-1].strip())

    except FileNotFoundError:
        return None

    except json.JSONDecodeError:
        return None


def get_status(buffer_usage, latency):

    if buffer_usage > 90 or latency > 4:
        return "CRITICAL"

    elif buffer_usage > 70 or latency > 2.5:
        return "WARNING"

    return "NORMAL"


def main(stdscr):

    global total_orders_processed
    global dashboard_refreshes

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(500)

    while True:

        data = read_latest_json()

        if data is None:
            data = {
                "orders": 0,
                "buffer": 0,
                "latency": 0.0
            }

        dashboard_refreshes += 1

        total_orders_processed += data["orders"]

        latency_history.append(data["latency"])

        avg_latency = sum(latency_history) / len(latency_history)
        max_latency = max(latency_history)
        min_latency = min(latency_history)

        status = get_status(
            data["buffer"],
            data["latency"]
        )

        orders_per_second = data["orders"]

        stdscr.clear()

        stdscr.addstr(
            0,
            0,
            "========== ChronosMatch Dashboard =========="
        )

        # Core Metrics
        stdscr.addstr(
            2,
            0,
            f"Orders Received : {data['orders']}"
        )

        stdscr.addstr(
            3,
            0,
            f"Buffer Usage    : {data['buffer']}%"
        )

        stdscr.addstr(
            4,
            0,
            f"Latency         : {data['latency']:.2f} ms"
        )

        # Status System
        stdscr.addstr(
            6,
            0,
            f"Engine Status   : {status}"
        )

        # Alerts
        stdscr.addstr(
            8,
            0,
            "============= ALERTS ============="
        )

        alert_row = 10
        alert_found = False

        if data["latency"] > 2.5:
            stdscr.addstr(alert_row, 0, "HIGH LATENCY ALERT")
            alert_row += 1
            alert_found = True

        if data["buffer"] > 80:
            stdscr.addstr(alert_row, 0, "BUFFER OVERFLOW RISK")
            alert_row += 1
            alert_found = True

        if not alert_found:
            stdscr.addstr(alert_row, 0, "System Operating Normally")

        # Day 11 Latency Monitoring
        stdscr.addstr(
            15,
            0,
            "========= LATENCY METRICS ========="
        )

        stdscr.addstr(
            17,
            0,
            f"Current Latency : {data['latency']:.2f} ms"
        )

        stdscr.addstr(
            18,
            0,
            f"Average Latency : {avg_latency:.2f} ms"
        )

        stdscr.addstr(
            19,
            0,
            f"Maximum Latency : {max_latency:.2f} ms"
        )

        stdscr.addstr(
            20,
            0,
            f"Minimum Latency : {min_latency:.2f} ms"
        )

        # Day 12 Performance Metrics
        stdscr.addstr(
            22,
            0,
            "======= PERFORMANCE METRICS ======="
        )

        stdscr.addstr(
            24,
            0,
            f"Total Orders Processed : {total_orders_processed}"
        )

        stdscr.addstr(
            25,
            0,
            f"Orders Per Second      : {orders_per_second}"
        )

        stdscr.addstr(
            26,
            0,
            f"Dashboard Refreshes    : {dashboard_refreshes}"
        )

        stdscr.addstr(
            28,
            0,
            "Press CTRL+C to Exit"
        )

        stdscr.refresh()
        time.sleep(1)


curses.wrapper(main)
