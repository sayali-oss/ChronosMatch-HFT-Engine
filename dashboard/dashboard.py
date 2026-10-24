import curses
import json
import time


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


def main(stdscr):

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

        stdscr.clear()

        stdscr.addstr(0, 0, "=== ChronosMatch Dashboard ===")

        stdscr.addstr(2, 0, f"Orders Received : {data['orders']}")
        stdscr.addstr(3, 0, f"Buffer Usage    : {data['buffer']}%")
        stdscr.addstr(4, 0, f"Latency         : {data['latency'\]:.2f} ms")

        stdscr.addstr(6, 0, "ALERTS")
        stdscr.addstr(7, 0, "------------------------")

        row = 8

        # Alert 1
        if data["latency"] > 2.5:
            stdscr.addstr(row, 0, "HIGH LATENCY ALERT")
            row += 1

        # Alert 2
        if data["buffer"] > 80:
            stdscr.addstr(row, 0, "BUFFER OVERFLOW RISK")
            row += 1

        # Normal State
        if data["latency"] <= 2.5 and data["buffer"] <= 80:
            stdscr.addstr(row, 0, "System Operating Normally")

        stdscr.refresh()
        time.sleep(1)


curses.wrapper(main)


