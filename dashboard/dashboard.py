import curses
import time

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)
    stdscr.timeout(500)

    orders = 0
    buffer_usage = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "ChronosMatch Dashboard")
        stdscr.addstr(2, 0, "Orders received: {orders}")
        stdscr.addstr(3, 0, "Buffer usage: {buffer_usage}%")
        stdscr.addstr(4, 0, "Latency: TBD")

        stdscr.refresh()
        time.sleep(1)

# Simulate updates
        orders += 1
        buffer_usage = (buffer_usage + 5) % 101  # cycles 0–100%
curses.wrapper(main)
