import curses
import time
import json

def read_latest_json(filename="engine.json"):
    """Read the last JSON entry from the log file"""
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            if lines:
                return json.loads(lines[-1].strip())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    return None

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(500)

    while True:
        # Read latest JSON log entry
        data = read_latest_json()
        if not data:
            data = {"orders": 0, "buffer": 0, "latency": 0.0}

        stdscr.clear()
        stdscr.addstr(0, 0, "ChronosMatch Dashboard (Day 8)")
        stdscr.addstr(2, 0, f"Orders received: {data['orders']}")
        stdscr.addstr(3, 0, f"Buffer usage: {data['buffer']}%")
        stdscr.addstr(4, 0, f"Latency: {data['latency']:.2f} ms")

        # --- Alerts Section ---
        alert_line = 6
        if data['latency'] > 2.5:
            stdscr.addstr(alert_line, 0, "⚠ High Latency!", curses.A_BOLD)
            alert_line += 1
        if data['buffer'] > 80:
            stdscr.addstr(alert_line, 0, "⚠ Buffer Overflow Risk!", curses.A_BOLD)

        stdscr.refresh()
        time.sleep(1)
      
curses.wrapper(main)


