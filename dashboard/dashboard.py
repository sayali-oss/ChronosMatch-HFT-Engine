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

    else:
        return "NORMAL"


def get_grade(avg_latency):

    if avg_latency < 1:
        return "A+"

    elif avg_latency < 2:
        return "A"

    elif avg_latency < 3:
        return "B"

    return "C"


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

        throughput_score = orders_per_second * 10

        efficiency = max(
            0,
            min(
                100,
                100 - data["latency"] * 10
            )
        )

        grade = get_grade(avg_latency)

        stdscr.clear()

        stdscr.addstr(
            0,
            0,
            "========== ChronosMatch Dashboard =========="
        )

        # Core Metrics
        stdscr.addstr(2, 0, f"Orders Received : {data['orders']}")
        stdscr.addstr(3, 0, f"Buffer Usage    : {data['buffer']}%")
        stdscr.addstr(4, 0, f"Latency         : {data['latency'\]:.2f} ms")

        # Status
        stdscr.addstr(6, 0, f"Engine Status   : {status}")

        # Alerts
        stdscr.addstr(8, 0, "============= ALERTS =============")

        row = 10
        alert_found = False

        if data["latency"] > 2.5:
            stdscr.addstr(row, 0, "HIGH LATENCY ALERT")
            row += 1
            alert_found = True

        if data["buffer"] > 80:
            stdscr.addstr(row, 0, "BUFFER OVERFLOW RISK")
            row += 1
            alert_found = True

        if not alert_found:
            stdscr.addstr(row, 0, "System Operating Normally")

        # Latency Panel
        stdscr.addstr(15, 0, "========= LATENCY METRICS =========")

        stdscr.addstr(17, 0, f"Current Latency : {data['latency'\]:.2f} ms")
        stdscr.addstr(18, 0, f"Average Latency : {avg_latency:.2f} ms")
        stdscr.addstr(19, 0, f"Maximum Latency : {max_latency:.2f} ms")
        stdscr.addstr(20, 0, f"Minimum Latency : {min_latency:.2f} ms")

        # Performance Metrics
        stdscr.addstr(22, 0, "======= PERFORMANCE METRICS =======")

        stdscr.addstr(24, 0, f"Total Orders Processed : {total_orders_processed}")
        stdscr.addstr(25, 0, f"Orders Per Second      : {orders_per_second}")
        stdscr.addstr(26, 0, f"Dashboard Refreshes    : {dashboard_refreshes}")

        # Day 13 Section
        stdscr.addstr(28, 0, "======= BENCHMARK STATISTICS =======")

        stdscr.addstr(30, 0, f"Throughput Score : {throughput_score}")
        stdscr.addstr(31, 0, f"Engine Efficiency: {efficiency:.2f}%")
        stdscr.addstr(32, 0, f"Performance Grade: {grade}")

        stdscr.addstr(34, 0, "Press CTRL+C to Exit")

        stdscr.refresh()
        time.sleep(1)


curses.wrapper(main)
