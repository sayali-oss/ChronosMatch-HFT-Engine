
import cProfile
import pstats
from pathlib import Path

from firehose.order_generator import generate_order
from matching_engine import MatchingEngine


def profile_matching_only(total_orders=10_000):
    # Generate orders before profiling begins.
    orders = [
        generate_order(order_id)
        for order_id in range(1, total_orders + 1)
    ]

    engine = MatchingEngine()

    profiler = cProfile.Profile()
    profiler.enable()

    for order in orders:
        engine.add_order(order)

    profiler.disable()

    print("\n===== MATCHING-ONLY PROFILE =====")
    print(f"Orders processed : {total_orders:,}")
    print(f"Trades executed  : {len(engine.trades):,}")
    print(f"Open BUY orders  : {len(engine.buy_orders):,}")
    print(f"Open SELL orders : {len(engine.sell_orders):,}")

    print("\n===== TOP FUNCTIONS BY CUMULATIVE TIME =====")
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)

    output_file = Path("matching_only_profile.prof")
    profiler.dump_stats(str(output_file))
    print(f"\nProfile saved to : {output_file.resolve()}")


if __name__ == "__main__":
    profile_matching_only()

