import curses
import time

def read_latest_log_line(filename="engine.log"):
    """Read the last line from the log file"""
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            if lines:
                return lines[-1].strip()
    except FileNotFoundError:
        return None
    return None

def parse_log_line(line):
    """Convert log line into a dictionary of metrics"""
    data = {"orders": 0, "buffer": 0, "latency": 0.0}
    if line:
        parts = line.split()
        for part in parts:
            key, value = part.split("=")
            if key == "orders":
                data["orders"] = int(value)
            elif key == "buffer":
                data["buffer"] = int(value)
            elif key == "latency":
                data["latency"] = float(value)
    return data

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(500)

    while True:
        # Read latest log entry
        line = read_latest_log_line()
        data = parse_log_line(line)

        stdscr.clear()
        stdscr.addstr(0, 0, "ChronosMatch Dashboard (Day 6)")
        stdscr.addstr(2, 0, f"Orders received: {data['orders']}")
        stdscr.addstr(3, 0, f"Buffer usage: {data['buffer']}%")
        stdscr.addstr(4, 0, f"Latency: {data['latency']:.2f} ms")

        stdscr.refresh()
        time.sleep(1)

curses.wrapper(main)

