import curses
import time
import random

def get_mock_data():
    """simulate incoming data feed"""
    return {
        "orders": random.randint(50, 200),
        "buffer": random.randint(0, 100),
        "latency": random.uniform(0.5, 5.0)
    }
    
def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)
    stdscr.timeout(500)

    orders = 0
    buffer_usage = 0
    latency = 0.0
    
       while True:
        # Fetch mock data
        data = get_mock_data()

        stdscr.clear()
        stdscr.addstr(0, 0, "ChronosMatch Dashboard")
        stdscr.addstr(2, 0, f"Orders received: {data['orders']}")
        stdscr.addstr(3, 0, f"Buffer usage: {data['buffer']}%")
        stdscr.addstr(4, 0, f"Latency: {data['latency']:.2f} ms")

        stdscr.refresh()
        time.sleep(1)

curses.wrapper(main)
