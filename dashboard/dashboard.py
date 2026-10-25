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


def get_status(buffer_usage, latency):

    if buffer_usage > 90 or latency > 4:
        return "CRITICAL"

    elif buffer_usage > 70 or latency > 2.5:
        return "WARNING"

    else:
        return "NORMAL"


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

        status = get_status(
            data["buffer"],
            data["latency"]
        )

        stdscr.clear()

        stdscr.addstr(
            0,
            0,
            "============== ChronosMatch Dashboard =============="
        )

        stdscr.addstr(2, 0, f"Orders Received : {data['orders']}")
        stdscr.addstr(3, 0, f"Buffer Usage    : {data['buffer']}%")
        stdscr.addstr(4, 0, f"Latency         : {data['latency'\]:.2f} ms")

        stdscr.addstr(
            6,
            0,
            f"Engine Status   : {status}"
        )

        stdscr.addstr(8, 0, "--------------- ALERTS ---------------")

        row = 10

        alert_found = False

        if data["latency"] > 2.5:
            stdscr.addstr(
                row,
                0,
                "HIGH LATENCY ALERT"
            )
            row += 1
            alert_found = True

        if data["buffer"] > 80:
            stdscr.addstr(
                row,
                0,
                "BUFFER OVERFLOW RISK"
            )
            row += 1
            alert_found = True

        if not alert_found:
            stdscr.addstr(
                row,
                0,
                "System Operating Normally"
            )

        stdscr.addstr(
            15,
            0,
            "Press CTRL+C to exit"
        )

        stdscr.refresh()
        time.sleep(1)


curses.wrapper(main)

